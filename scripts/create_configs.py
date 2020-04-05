# Moves all image label pairs into one directory: Dataset_onedir
import os
import glob

col_grn = '\033[92m'
col_end = '\033[0m'
col_blue = '\033[94m'

def create_cfg(cfg_dir_path):
    # Read cfg/yolov3.cfg file
    f = open(cfg_dir_path + 'yolov3.cfg', 'r')
    lines = f.readlines()
    f.close
    new_lines = []
    for ln in lines:
        if 'max_batches' in ln:
            new_lines.append('max_batches=4000\n') # classes*2000 and >=4000
        elif 'steps=' in ln:
            new_lines.append('steps=3200,3600\n') # 80%,90% of max_batches
        elif 'classes' in ln:
            new_lines.append('classes=1\n')
        elif 'filters=255\n' in ln:
            new_lines.append('filters=18\n') # filters = 3*(classes+5)
        else:
            new_lines.append(ln)
    # Write new cfg/yolov3-custom.cfg file
    cfg_path = cfg_dir_path + 'yolov3-custom.cfg'
    f = open(cfg_path, 'w')
    f.writelines(new_lines)
    f.close
    print('Created (3/5): ' + cfg_path)

    return cfg_path

def create_lists(dataset_dir_path):
    # Create train.txt list
    train_path = dataset_dir_path + 'Train/'
    train_list = train_path + 'train.txt'
    train_images = list(glob.iglob(train_path + '**/*.jpg', recursive=True))
    f = open(train_list, 'w')
    f.writelines(map(lambda x: x + '\n', train_images))
    f.close
    print('Created (1/6): ' + train_list)

    # Create test.txt list
    test_path = dataset_dir_path + 'Test/'
    test_list = test_path + 'test.txt'
    test_images = list(glob.iglob(test_path + '**/*.jpg', recursive=True))
    f = open(test_list, 'w')
    f.writelines(map(lambda x: x + '\n', test_images))
    f.close
    print('Created (2/6): ' + test_list)
    
     # Create valid.txt list
    valid_path = dataset_dir_path + 'Valid/'
    valid_list = valid_path + 'valid.txt'
    valid_images = list(glob.iglob(valid_path + '**/*.jpg', recursive=True))
    f = open(valid_list, 'w')
    f.writelines(map(lambda x: x + '\n', valid_images))
    f.close
    print('Created (3/6): ' + valid_list)

    return train_list, test_list

def create_configs(dataset_dir_path):
    print('Creating required config files')

    darknet_path = os.getcwd()
    train_list, test_list = create_lists(dataset_dir_path)
    cfg_dir_path = darknet_path + '/cfg/'
    cfg_path = create_cfg(cfg_dir_path)
    
    # Create data/classes.names file
    names_list = darknet_path + '/data/classes.names'
    lines = ['vehicle']
    f = open(names_list, 'w')
    f.writelines(lines)
    f.close
    print('Created (4/5): ' + names_list)

    # Create cfg/config.data file
    config = cfg_dir_path + 'custom.data'
    lines = ['classes = 1\n',
            'train = ' + train_list + '\n',
            'valid = ' + test_list + '\n',
            'names = ' + names_list + '\n',
            'backup = backup']
    f = open(config, 'w')
    f.writelines(lines)
    f.close
    print('Created (5/5): ' + config)
    print()

    # Display training instructions
    print('Instructions')
    print('(To use with GPU) Change the first line of the Makefile in the base directory to GPU=1 and run >> '
            + col_blue + 'make' + col_end)
    print('Download the pretrained weights in the base directory using the command')
    print('>> ' + col_blue + 'wget https://pjreddie.com/media/files/darknet53.conv.74' + col_end)
    config_rel = os.path.relpath(config, darknet_path)
    cfg_rel = os.path.relpath(cfg_path, darknet_path)
    print('To start the training use command')
    print('>> ' + col_blue + './darknet detector train ' + config_rel + ' ' + cfg_rel + ' darknet53.conv.74 -map' + col_end)


if __name__ == "__main__":
    # Get file path of the dataset directory
    dataset_dir_path = input(col_grn + 'Enter file path for the dataset directory: \n>> ' + col_end)
    # If abs_path input does not begin with '/' assume it is a relative path
    if dataset_dir_path[:1] != '/':
        dataset_dir_path = os.getcwd() + '/' + dataset_dir_path + '/'
    else:
        dataset_dir_path = dataset_dir_path + '/'
    create_configs(dataset_dir_path)
