import os
import cv2
import glob
import numpy as np
from tqdm import tqdm

def output_video(images, filename):
    frames = []
    for img in images:
        frames.append(cv2.imread(img))
        frames.append(cv2.imread(img))
        frames.append(cv2.imread(img))
        frames.append(cv2.imread(img))
        frames.append(cv2.imread(img))
    height, width, layers = frames[0].shape
    size = (width, height)
    out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'DIVX'), 25, size)
    for frame in frames:
        out.write(frame)
    out.release()
    
def create_videos(old_dir_path, new_dir_path):
    print('Creating videos in "../darknet/data/Dataset/Videos"')

    # Create dirs
    video_path = new_dir_path + 'Videos/'
    os.rmdir(video_path)
    os.makedirs(video_path)

    # Get sub dirs and files
    tree = list(os.walk(old_dir_path))

    for branch in tqdm(tree):
        # If no more sub dirs (end of branch)
        if branch[1] == []:
            images = list(glob.iglob(branch[0] + '/*.jpg'))
            images.sort()
            name = os.path.split(os.path.dirname(images[0]))[1]
            filename = video_path + name + '.avi'
            output_video(images, filename)

create_videos('/home/fg/Documents/QFreeDatasets/', '/home/fg/Documents/darknet/data/Dataset/')
