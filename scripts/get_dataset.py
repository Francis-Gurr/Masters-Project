# Moves all image label pairs into one directory: Dataset_onedir
import os
import glob
import shutil
from tqdm import tqdm
#from create_videos import create_videos
from create_configs import create_configs

col_warn = '\033[93m'
col_grn = '\033[92m'
col_end = '\033[0m'

# Change label to have only one class and remove cycle and pedestrian
def reclassify(label):
    new_label = []
    f = open(label, 'r')
    for line in f:
        if int(line[:1]) < 9:
            new_label.append('0' + line[1:])
    f.close()
    return new_label

# Create the "../New_Dataset" directory, and delete it if it already exists
new_dir_path = os.getcwd() + '/data/Dataset/'
if os.path.exists(new_dir_path):
    ip = input(col_warn + 'Warning: Will delete existing "../darknet/data/Dataset" directory! \nPress "x" to abort or any other key to continue: \n>> ' + col_end)
    if ip == 'x' or ip =='X':
        print('Exiting')
        exit()
    else:
        print('Deleting "../darknet/data/Dataset" directory')
        shutil.rmtree(new_dir_path)
        print('Deleted')
train_path = new_dir_path + 'Train/'
valid_path = new_dir_path + 'Valid/'
unlabelled_path = new_dir_path + 'Unlabelled/'
os.makedirs(train_path)
os.makedirs(valid_path)
os.makedirs(unlabelled_path)

# Get file path of the dataset directory
old_dir_path = input(col_grn + 'Enter file path for the current dataset directory: \n>> ' + col_end)
# If old_dir_path input does not begin with '/' assume it is a relative path
if old_dir_path[:1] != '/':
    old_dir_path = os.getcwd() + '/' + old_dir_path + '/'
else:
    old_dir_path = old_dir_path + '/'

# Get proportion to training and validation data
prop = int(input(col_grn + 'Enter the proportion of training to validation data (0 < int < 10): \n>> ' + col_end))

print('Creating "../darknet/data/Dataset"')

# Get list of all the image and label paths
images = list(glob.iglob(old_dir_path + '**/*.jpg', recursive=True))
labels = list(glob.iglob(old_dir_path + '**/*.txt', recursive=True))
images.sort()
labels.sort()

i = 0
i_train = 0
i_valid = 0
i_unlabelled = 0
for img in tqdm(images):
    base = os.path.splitext(img)[0]
    lbl = base + '.txt'
    new_file_path = ''
    # If label exists move image label pair to the new directory
    if lbl in labels:
        if i%10 < prop:
            # Training set
            new_file_path = '%strain_%05d' % (train_path, i_train)
            i_train+=1
        else:
            # Validation set
            new_file_path = '%svalid_%05d' % (valid_path, i_valid)
            i_valid+=1
        
        # Edit label to contain only one class and write to new database directory
        new_label = reclassify(lbl)
        f = open(new_file_path + '.txt', 'w')
        f.writelines(new_label)
        f.close()
        i+=1
    else:
        new_file_path = '%sunlabelled_%05d' % (unlabelled_path, i_unlabelled)
        i_unlabelled+=1
    
    # Copy image to new database directory
    shutil.copy(img, new_file_path + '.jpg')

#create_videos(old_dir_path, new_dir_path)
create_configs(new_dir_path)
