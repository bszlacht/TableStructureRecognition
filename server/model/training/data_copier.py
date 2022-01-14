from shutil import copyfile
from os import listdir
from os import path
import os

# This file will be deleted in the future


img_path = "images/"
ann_path = "annotations/"


# Helper functions to copy files from external drive
def copy_files():
    file = open('image_names.txt')
    src = "/media/aneta/External_Drive/PubTables1M-Detection-PASCAL-VOC/"
    dest = "data/"
    it = 0
    not_found = 0
    for line in file.readlines():
        line = line.strip()
        # img_name, rest = line.split('_')
        # rest, img_name = img_name.split('/')
        # img_name += "_tables.json"
        s = src + line
        d = dest + line
        try:
            copyfile(s, d)
        except FileNotFoundError:
            not_found += 1

        it += 1
        if it % 1000 == 0:
            print(it)
    file.close()
    print(not_found)


def delete_missing():
    deleted = 0
    for file in listdir(img_path):
        img_name, rest = file.split('_')
        img_name += "_tables.json"
        p = ann_path + img_name
        if not path.exists(p):
            deleted += 1
            d = img_path + file
            os.remove(d)

    print(deleted)


def list_images():
    f = open("image_lists/images_list.txt", 'w')

    for file in listdir(img_path):
        f.writelines(file + '\n')

    f.close()


def split_images(train_size=0.8, test_size=0.1):
    f = open("image_lists/images_list.txt", 'r')
    f_training = open("image_lists/training.txt", 'w')
    f_test = open("image_lists/test.txt", 'w')
    f_val = open("image_lists/val.txt", 'w')

    images_number = 33555
    train_idx = images_number * train_size
    test_idx = images_number * (test_size + train_size)

    it = 0
    for line in f.readlines():
        if it < train_idx:
            f_training.writelines(line)
        elif it < test_idx:
            f_test.writelines(line)
        else:
            f_val.writelines(line)
        it += 1

    f.close()
    f_training.close()
    f_test.close()
    f_val.close()


# copy_files()
# delete_missing()
# list_images()
# split_images()
