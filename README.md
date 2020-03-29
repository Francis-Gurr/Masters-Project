# Calcualting the speed of vehicles from video images using machine learning

This work uses darknet and YOLO for the object detection.
YOLO is implemented using AlexayAB's darknet repository: [link]()

### Requirements
* Cuda 10
* cuDNN 7 - possibly not necessary but everything was ran with cuDNN so cannot say for sure
* OpenCV 4
* CMake 3.8
* Python3 - and the tqdm module (pip3 install tqdm)

### Steps
##### 1. Download AlexayAB's darknet repository

```
git clone https://github.com/AlexeyAB/darknet.git
```

##### 2. Make the repository
  Set the following options in the Makefile
  ```
  GPU=1
  CUDNN=1
  OPENCV=1
  LIBSO=1
  ```
  Then inside the darknet root directory run
  ```
  mkdir build-release
  cd build-release
  cmake ..
  make
  make install
  ```
  Alternatively just using `make` may also work

  
