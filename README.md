# Calcualting the speed of vehicles from video images using machine learning

This work uses darknet and YOLO for the object detection.
YOLO is implemented using AlexayAB's darknet repository: [link]()

The requirements are:
* Cuda 10
* cuDNN 7 - possibly not necessary but everything was ran with cuDNN so cannot say for sure
* OpenCV 4
* CMake 3.8
* Python3 - and the tqdm module (pip3 install tqdm)

Steps
1. Download AlexayAB's darknet repository
'''
git clone https://github.com/AlexeyAB/darknet.git
'''
2. Make the repository
