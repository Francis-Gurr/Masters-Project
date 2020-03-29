import cv2
import argparse
from math import pi
from math import sin
from math import cos
from math import tan
from math import asin
from math import atan
from math import atan2
from math import sqrt
from math import degrees
from math import radians

img_w = -1
img_h = -1
drawing = False
i_label = 0
label_list = ["A", "B", "C", "D"]
history = []
x_2D = []
y_2D = []
WL = [-1, -1]
camera_params = []

###################################################################################################
# THE MATHS

# Get 3D world coords from 2D image coordinates
def get_XY_3D(x_2D, y_2D):
    global img_w, img_h, camera_params
    # Reparametrise coordinates
    x_2D = x_2D - img_w/2
    y_2D = -(y_2D - img_h/2)
    
    s = camera_params[0]
    t = camera_params[1]
    p = camera_params[2]
    f = camera_params[3]
    h = camera_params[4]
    a = x_2D*sin(s) + y_2D*cos(s)
    b = x_2D*cos(s) - y_2D*sin(s)
    den = x_2D*cos(t)*sin(s) + y_2D*cos(t)*cos(s) + f*sin(t)

    #Yung and He - wrong?
    #X_3D = ((h*sin(p)*a) / (sin(t) + h*cos(p)*b)) / den
    #Y_3D = ((-h*cos(p)*a) / (sin(t) + h*sin(p)*b)) / den
    # Corrected Yung and He
    X_3D = (((h*sin(p)*a) / sin(t)) + h*cos(p)*b) / den
    Y_3D = (((-h*cos(p)*a) / sin(t)) + h*sin(p)*b) / den
    #using l not h
    #X_3D = ((-l*sin(p)*a) + (sin(t) * l*cos(p)*b)) / den
    #Y_3D = ((-l*cos(p)*a) + (sin(t) * l*sin(p)*b)) / den

    return (X_3D, Y_3D)

# Reparameterised coordinate system (moved the image plane origin from top left to centre and flipped the y axis)
def reparam_coords():
    global x_2D, y_2D, img_h, img_w
    for i in range(4):
        x_2D[i] = x_2D[i] - img_w/2
        y_2D[i] = -(y_2D[i] - img_h/2)

# Calculate variables
def get_abc():
    global x_2D, y_2D

    a = (x_2D[1]-x_2D[0], x_2D[2]-x_2D[0], x_2D[3]-x_2D[1], x_2D[3]-x_2D[2])
    b = (y_2D[1]-y_2D[0], y_2D[2]-y_2D[0], y_2D[3]-y_2D[1], y_2D[3]-y_2D[2])
    c = ((x_2D[0]*y_2D[1]-x_2D[1]*y_2D[0], x_2D[0]*y_2D[2]-x_2D[2]*y_2D[0],
          x_2D[1]*y_2D[3]-x_2D[3]*y_2D[1], x_2D[2]*y_2D[3]-x_2D[3]*y_2D[2]))
    return a, b, c

# Calculate variables
def get_uv(s, reordered = False):
    global x_2D, y_2D, WL
    u = []
    v = []
    for i in range(4):
        u.append(x_2D[i]*sin(s) + y_2D[i]*cos(s))
        v.append(x_2D[i]*cos(s) - y_2D[i]*sin(s))

    if reordered:
        WL = [WL[1], WL[0]]
        x_2D = [x_2D[2], x_2D[0], x_2D[3], x_2D[1]]
        y_2D = [y_2D[2], y_2D[0], y_2D[3], y_2D[1]]

    return u, v

# Calculate the swing angle
def get_s(a, b, c):
    num = ((b[2]*b[3]*a[1]*c[0]) - (b[1]*b[3]*a[2]*c[0])
         + (b[0]*b[2]*a[3]*c[1]) - (b[2]*b[3]*a[0]*c[1])
         + (b[1]*b[3]*a[0]*c[2]) - (b[0]*b[1]*a[3]*c[2])
         + (b[0]*b[1]*a[2]*c[3]) - (b[0]*b[2]*a[1]*c[3]))

    den = ((a[2]*a[3]*b[1]*c[0]) - (a[1]*a[3]*b[2]*c[0])
         + (a[0]*a[2]*b[3]*c[1]) - (a[2]*a[3]*b[0]*c[1])
         + (a[1]*a[3]*b[0]*c[2]) - (a[0]*a[1]*b[3]*c[2])
         + (a[0]*a[1]*b[2]*c[3]) - (a[0]*a[2]*b[1]*c[3]))

    s = atan2(num, den)
    return s

# Calculate the camera parameters using Fung and Yung's method
def FY(a, b, c, s):
    global x_2D, y_2D, WL

    # Calculate the tilt angle
    num = (((a[2]*c[1]-a[1]*c[2])*sin(s) + (b[2]*c[1]-b[1]*c[2])*cos(s)) *
           ((a[3]*c[0]-a[0]*c[3])*sin(s) + (b[3]*c[0]-b[0]*c[3])*cos(s)))
    den = (((a[3]*c[0]-a[0]*c[3])*cos(s) + (b[0]*c[3]-b[3]*c[0])*sin(s)) *
           ((b[2]*c[1]-b[1]*c[2])*sin(s) + (a[1]*c[2]-a[2]*c[1])*cos(s)))

    # Bodge :(
    nd = num/den
    if nd < 0:
        print("Bodge")
        nd = -nd

    t = asin(-sqrt(nd))

    # Calculate the pan angle
    num = sin(t) * ((b[2]*c[1]-b[1]*c[2])*sin(s) + (a[1]*c[2]-a[2]*c[1])*cos(s))

    den = (a[2]*c[1]-a[1]*c[2])*sin(s) + (b[2]*c[1]-b[1]*c[2])*cos(s)

    p = atan2(num, den)

    # Calculate the focal length
    num = c[2] * cos(p) * cos(t)

    den = (b[2]*sin(p)*cos(s) - b[2]*cos(p)*sin(t)*sin(s)
         + a[2]*sin(p)*sin(s) + a[2]*cos(p)*sin(t)*cos(s))

    f = num / den

    # Calculate the camera height
    num = WL[0] * (f*sin(t) + x_2D[0]*cos(t)*sin(s) + y_2D[0]*cos(t)*cos(s)) * (f*sin(t) + x_2D[2]*cos(t)*sin(s) + y_2D[2]*cos(t)*cos(s))

    den = (-(f*sin(t) + x_2D[0]*cos(t)*sin(s) + y_2D[0]*cos(t)*cos(s)) *
            (x_2D[2]*cos(p)*sin(s) - x_2D[2]*sin(p)*sin(t)*cos(s) + y_2D[2]*cos(p)*cos(s) + y_2D[2]*sin(p)*sin(t)*sin(s))
           +(f*sin(t) + x_2D[2]*cos(t)*sin(s) + y_2D[2]*cos(t)*cos(s)) *
            (x_2D[0]*cos(p)*sin(s) - x_2D[0]*sin(p)*sin(t)*cos(s) + y_2D[0]*cos(p)*cos(s) + y_2D[0]*sin(p)*sin(t)*sin(s)))

    h = sin(t) * num/den

    #if f < 0:
    #    f = -f
    #    s = s + pi
    #if h < 0:
    #    h = -h
    #    p = p + pi

    return [s, t, p, f, h]

# Calculate the camera parameters using He and Yung's method
def HY(u, v, s, reordered = False):
    global WL

    # Calculate the tilt angle
    # Calculate F
    num = ((v[0]*u[1]-v[1]*u[0]) * (u[2]-u[3])) - ((v[2]*u[3]-v[3]*u[2]) * (u[0]-u[1]))
    den = ((v[0]-v[1]) * (u[2]-u[3])) - ((v[2]-v[3]) * (u[0]-u[1]))
    F = -(num/den)

    # Calculate t1
    num = ((u[0]*(u[1]+F)*(u[2]+F) - u[2]*(u[0]+F)*(u[1]+F)) -
           (v[0]*(u[1]+F)*(u[2]+F) - v[2]*(u[0]+F)*(u[1]+F)) *
           (((u[0]-u[1])*F) / (v[0]*u[1] - v[1]*u[0] + (v[0]-v[1])*F)))
    den  = v[0]*(u[1]+F)*(u[2]+F) - v[1]*(u[0]+F)*(u[2]+F)
    t1 = ((WL[1]/WL[0]) * num) / den

    # Calculate t2
    num = ((u[0]*(u[1]+F)*(u[2]+F) - u[1]*(u[0]+F)*(u[2]+F)) *
          (((u[0]-u[1])*F) / (v[0]*u[1] - v[1]*u[0] + (v[0]-v[1])*F)))
    t2 = num/den

    t = (-t1 + sqrt(t1**2 - 4*t2)) / 2
    if (t <= -1 or t >= 0):
        t = (-t1 - sqrt(t1**2 - 4*t2)) / 2
    t = asin(t)

    # Calculate the focal length
    f = F/tan(t)
    #if f < 0:
    #    f = -f
    #    s = s + pi
    #    u,v = get_uv(s)

    # Calculate the pan angle
    num = (u[0] - u[1]) * f * tan(t)
    den = v[0]*u[1] - v[1]*u[0] + (v[0] - v[1]) * f * tan(t)
    p = atan2((1/sin(t)) * num, den)

    # Calculate the height of the camera
    num = (WL[0]*cos(t)*sin(t)) / cos(p)
    den = (((sin(t)*tan(p)*v[2] - u[2]) / (u[2] + f*tan(t))) -
           ((sin(t)*tan(p)*v[0] - u[0]) / (u[0] + f*tan(t))))
    h = num/den

    #if h < 0:
    #    h = -h
    #    p = p + pi

    if reordered:
        # Do something
        print()
    
    return [s, t, p, f, h]

# Write the camera parameters to file
def write_to_file(cam_stpfh):
    lines = ["swing=%f\n" % cam_stpfh[0], "tilt=%f\n" % cam_stpfh[1], "pan=%f\n" % cam_stpfh[2], "focal=%f\n" % cam_stpfh[3], "height=%f\n" % cam_stpfh[4]]
    fp = open("cfg/cam_params.txt", "w")
    fp.writelines(lines)
    fp.close()

# Get the camera parameters and write them to file
def get_cam_params():
    global camera_params
    # Reparameterise coordinate system
    reparam_coords()

    # Get an initial value of the pan angle using Fung and Yungs method
    WL[0] = 3.65
    a, b, c = get_abc()
    s = get_s(a, b, c)
    cam_stpfh = FY(a, b, c, s)
    p = degrees(cam_stpfh[2])

    # Use the initial pan angle to decide which method to use
    if (p > 60 and p < 120):
        # HY
        WL[1] = float(input("\nGive the length (m) of the rectangle.\n"
                            "For UK roads refer to:\n"
                            "https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/773421/traffic-signs-manual-chapter-05.pdf)\n"
                            "Length: "))
        u, v = get_uv(s)
        cam_stpfh = HY(u, v, s)
    elif (p < 30 or p > 150):
        # HY reordered
        WL[1] = float(input("For UK roads refer to -\n"
                            "https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/773421/traffic-signs-manual-chapter-05.pdf\n"
                            "Give the length (m) of the rectangle: "))
        u, v = get_uv(s, reordered = True)
        cam_stpfh = HY(u, v, s, reordered = True)

    print("\nThe calculated camera parameters are:\n"
          "Swing angle (deg) = %f\n"
          "Tilt angle (deg) = %f\n"
          "Pan angle (deg) = %f\n"
          "Focal length (px) = %f\n"
          "Height (m) = %f"
          % (degrees(cam_stpfh[0]), degrees(cam_stpfh[1]), degrees(cam_stpfh[2]), cam_stpfh[3], cam_stpfh[4]))

    camera_params = cam_stpfh

    # Write the camera parameters to a file
    write_to_file(cam_stpfh)

###################################################################################################
# CLICK EVENT HANDLERS

def click_ref(event, x, y, flags, param):
    global drawing, i_label, label_list, history, x_2D, y_2D
    # If the left mouse button was clicked record the starting (x, y) coordinates
    if event == cv2.EVENT_LBUTTONDOWN:
        if i_label < 4:
            drawing = True
            # Draw a circle
            cv2.circle(image, (x,y), 3, (255, 0, 0), -1, cv2.LINE_AA)
            text = label_list[i_label] + " (" + str(x) + ", " + str(y) + ")"
            text_loc = (x-5, y+20)
            cv2.putText(image, text, text_loc, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,0,0), 1, cv2.LINE_AA)
            cv2.imshow("image", image)
            history.append(image.copy())
            x_2D.append(x)
            y_2D.append(y)
            i_label += 1

    # If the left mouse button was released record the ending (x, y) coordinates
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False

def click_test(event, x, y, flags, param):
    global drawing, camera_params
    # If the left mouse button was clicked record the starting (x, y) coordinates
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        # Draw a circle
        cv2.circle(image, (x,y), 3, (0, 0, 255), -1, cv2.LINE_AA)
        # Get 3D (X, Y) coords
        xy_3D = get_XY_3D(x, y)
        text = "(%.1f, %.1f)" % (xy_3D[0], xy_3D[1])
        text_loc = (x-5, y+20)
        cv2.putText(image, text, text_loc, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,255), 1, cv2.LINE_AA)
        cv2.imshow("image", image)

    # If the left mouse button was released record the ending (x, y) coordinates
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False

###################################################################################################
# MAIN

# Get the mean
def mean(a):
    return sum(a) / len(a)

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image")
args = vars(ap.parse_args())
####
def mean(a):
    return sum(a) / len(a)
print("Select points A,B,C,D that form a rectangle in the world plane where:\n"
      "Z=0, AB = CD and AC = BD\n")
print("Controls:\n"
      "Click to draw a point\n"
      "Press 'u' to undo a point\n"
      "Press 'r' to reset all the current points\n"
      "Press 'n' to draw another set of points to create an average\n"
      "Hit the return key when done\n")

# load the image, clone it, and setup the mouse callback function
image = cv2.imread(args["image"])
img_h = image.shape[0]
img_w = image.shape[1]
blank = image.copy()
history.append(image.copy())

cv2.namedWindow("image")
cv2.setMouseCallback("image", click_ref)

x_2D_list = []
y_2D_list = []
exit_flag = False
while not exit_flag:
    while True:
        # display the image and wait for a keypress
        cv2.imshow("image", image)
        key = cv2.waitKey(1) & 0xFF
        
        # if the 'r' key is pressed, reset the image
        if key == ord("r"):
            i_label = 0
            image = history[0].copy()
            history = [history.pop(0)]
            x_2D = []
            y_2D = []
        
        # if the 'u' key is pressed, undo
        if key == ord("u"):
            if i_label > 0:
                i_label -= 1
                history.pop()
                x_2D.pop()
                y_2D.pop()
                image = history[-1].copy()
        
        # if the 'n' key is pressed, clear and allow another set of ABCDs to be entered
        if key == ord("n"):
            break

        # if the 'carriage return' key is pressed, break from the loop
        if key == ord("\r"):
            exit_flag = True
            break
    
    i_label = 0
    image = history[0].copy()
    history = [history.pop(0)]
    if x_2D:
        x_2D_list.append(x_2D)
    if y_2D:
        y_2D_list.append(y_2D)
    x_2D = []
    y_2D = []

# Get averages
x_2D = list(map(mean, zip(*x_2D_list)))
y_2D = list(map(mean, zip(*y_2D_list)))

get_cam_params()

###################################################################################################
# TEST

print("\nTest by clicking points on the image to get the 3D world coordinates")
print("Press 'q' to exit")
image = blank.copy()
cv2.setMouseCallback("image", click_test)
while True:
    # Display the image and wait for a keypress
    cv2.imshow("image", image)
    key = cv2.waitKey(1) & 0xFF

    # If the 'q' key is pressed, break from the loop
    if key == ord("q"):
        break

# close all open windows
cv2.destroyAllWindows()
