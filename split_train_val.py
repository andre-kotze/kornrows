'''
script will split data from 'data' dir into:
├── images
│   ├── train
│   └── validation
└── labels
    ├── train
    └── validation

according to the percentage given

'''

import os
from os.path import join
import sys
import random
from shutil import copy
import glob

SPLIT = 0.1
copy = True # if false, moves (not implemented)

# set up directories
current_dir = os.getcwd()
data_dir = join(current_dir, 'data/')
if not os.path.exists(data_dir):
    print('Cannot find data dir')
    sys.exit(0)

dirs, subdirs = ['labels/', 'images/'], ['train/', 'validation/']

for dir in dirs:
    for subdir in subdirs:
        os.mkdir(join(dir, subdir))

# collect label (txt) files
data = list(glob.iglob(join(data_dir, "*.txt")))
print(f'Found {len(data)} files\nShuffling')

# randomise data
random.shuffle(data)

#split data
split_index = int(len(data) * SPLIT)
print(f'Splitting into test: {1-SPLIT}, train: {SPLIT}')
test_data = data[:split_index]
train_data = data[split_index:]

# create Yolo-readable data structure     
if copy: 
    print('Copying out')
    for name in train_data:
        copy(join(data_dir, name), join(current_dir, 'labels/train/'))
        copy(join(data_dir, name[:-3] + 'jpg'), join(current_dir, 'images/train/'))
    for name in test_data:
        copy(join(data_dir, name), join(current_dir, 'labels/validation/'))
        copy(join(data_dir, name[:-3] + 'jpg'), join(current_dir, 'images/validation/'))

# finish
print('[OK]')