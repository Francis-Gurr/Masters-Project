# Calcualting the speed of vehicles from video images using machine learning

This work uses darknet and YOLO for the object detection.
YOLO is implemented using AlexayAB's darknet repository: [link]()

## Requirements
* Cuda 10
* cuDNN 7 - possibly not necessary but everything was ran with cuDNN so cannot say for sure
* OpenCV 4
* CMake 3.8
* Python3 - and the tqdm module (pip3 install tqdm)

### Object Detection
##### 1. Download AlexayAB's darknet repository.

   ```
   git clone https://github.com/AlexeyAB/darknet.git
   ```

##### 2. Make the repository.

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
   Alternatively just running `make` instead may work

##### 3. Test the build.

   To test the build first download a pre-trained weight file
   ```
   wget https://pjreddie.com/media/files/yolov3.weights
   ```
   Then run
   ```
   ./darknet detect cfg/yolov3.cfg yolov3.weights data/dog.jpg
   ```
   Check the commandline output and the output _predictions.jpg_ file to ensure everything ran as expected.

##### 4. Download the custom scripts and place them in the _darknet/scripts_ folder.

##### 5. Create the dataset, test, training and config files.
   
   Run this from the darknet root dir
   ```
   python3 get_dataset.py
   ```
   Follow the instructions and enter the path to the raw dataset, the proportion of testing and validation sets.
   (Recommended: Training - 7, Test - 2, Validation - 1)
   The script will do the following:
      * Create a training, test and validation folder in _darknet/data/Dataset_
      * Flatten the category labels to be of only one singular class, and remove the cyclist and pedestrain classes.
      * Create all of the necessary config files: _darknet/cfg/yolov3-custom.cfg_, _darknet/cfg/custom.data, darknet/cfg/classes.names
      
##### 5. Start training.
   
   First download the _darknet53.conv.74_ weight file
   ```
   wget https://pjreddie.com/media/files/darknet53.conv.74
   ```
   Then start the training using the following command
   ```
   ./darknet detector train cfg/custom.data cfg/yolov3-custom.cfg darknet53.conv.74 -map
   ```
   
##### 5. Test the model.
   
   Test the model by running
   ```
   ./darknet detector test cfg/custom.data cfg/yolov3-custom.cfg backup/<weightfile>.weights
   ```
   The weight files are saved in the _darknet/backup_ folder
   
### Camera Calibration
   
   Instructions to be finished.
   See _Vehicle_Speed_Yolo/calibration_ files.
   
### Tracking
   
   Instructions to be finished.
   See _Vehicle_Speed_Yolo/yolo_dll.cpp file.

### Speed measurements
   
   Instructions to be finished.
   See _Vehicle_Speed_Yolo/yolo_dll.cpp file.
   
## Resources
   
   These instructions were written up post completion of the project and there may be some missing steps that were forgotten about.
   For any issues encountered during the training please see:
      *[AlexayAB/darknet/README.md](https://github.com/AlexeyAB/darknet/blob/master/README.md)
      *[PJReddie YOLO](https://pjreddie.com/darknet/yolo/)
   
   

  
