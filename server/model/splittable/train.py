from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from shutil import copyfile
from os import listdir
import xml.etree.ElementTree as ET
import pandas as pd

"""

Values for table1 and table2

- table1 lower margin
- table2 upper margin
- tables width difference
- tables margin left difference
- tables margin right difference

"""

img_path = "./data/images"
ann_path = "./data/annotations/"


def list_images():
    f = open("images_list.txt", 'w')

    for file in listdir(img_path):
        f.writelines(file + '\n')

    f.close()


def sort_images_names():
    f = open("images_list.txt", "r")
    sorted_f = open("sorted.txt", 'w')

    lines = f.readlines()
    lines = sorted(lines)
    for line in lines:
        sorted_f.writelines(line)

    f.close()
    sorted_f.close()


def copy_files():
    file = open('./images_list.txt')
    src = "/home/aneta/Pulpit/DP_proj_datasets/TNCR/dataset/merged/"
    for line in file.readlines():
        line = line.strip()
        img_name, rest = line.split('.')
        ann_name = img_name + ".xml"
        s = src + ann_name
        d = ann_path + ann_name
        try:
            copyfile(s, d)
        except FileNotFoundError:
            print("FILE NOT FOUND")

    file.close()


def calculate_x(img1, img2):
    ann_name = img1 + ".xml"
    annotation_file_name = ann_path + ann_name

    tree = ET.parse(annotation_file_name)
    root = tree.getroot()

    img1_height = int(root.find("size").find("height").text)
    img1_width = int(root.find("size").find("width").text)

    objects = root.findall('object')

    table1_xmin = int(objects[-1].find('bndbox').find('xmin').text)
    table1_ymin = int(objects[-1].find('bndbox').find('ymin').text)
    table1_xmax = int(objects[-1].find('bndbox').find('xmax').text)
    table1_ymax = int(objects[-1].find('bndbox').find('ymax').text)

    ann_name = img2 + ".xml"
    annotation_file_name = ann_path + ann_name

    tree = ET.parse(annotation_file_name)
    root = tree.getroot()

    img2_height = int(root.find("size").find("height").text)
    img2_width = int(root.find("size").find("width").text)

    objects = root.findall('object')

    table2_xmin = int(objects[0].find('bndbox').find('xmin').text)
    table2_ymin = int(objects[0].find('bndbox').find('ymin').text)
    table2_xmax = int(objects[0].find('bndbox').find('xmax').text)
    table2_ymax = int(objects[0].find('bndbox').find('ymax').text)

    return [
        (img1_height - table1_ymax) / table1_ymax,
        table2_ymin / table2_ymax,
        abs((table1_xmax - table1_xmin) - (table2_xmax - table2_xmin)) / table1_xmax,
        abs(table1_xmin - table2_xmin) / table1_xmax,
        abs((img2_width - table2_xmax) - (img1_width - table1_xmax)) / table1_xmax
    ]


def prepare_data():
    file = open('./images_list.txt')
    lines = file.readlines()
    lines.sort()

    X = []
    Y = []

    for i in range(len(lines) - 1):
        line = lines[i].strip()
        img_name1, rest1 = line.split('.')

        line = lines[i + 1].strip()
        img_name2, rest2 = line.split('.')

        x_val = calculate_x(img_name1, img_name2)

        X.append(x_val)

        if rest1 == "jpg" or rest2 == "jpg":
            Y.append(0)
        else:
            _, img1_page_num = img_name1.split('-')
            _, img2_page_num = img_name2.split('-')

            if int(img2_page_num) - int(img1_page_num) == 1:
                Y.append(1)
            else:
                Y.append(0)

    df = pd.DataFrame(X, columns=['lower_margin', 'upper_margin', 'width_diff', 'left_margin', 'right_margin'])
    df['target'] = Y
    file.close()

    return df


def train():
    data = prepare_data()
    X_train, X_test, Y_train, Y_test = train_test_split(data.drop(['target'], axis='columns'), data.target,
                                                        test_size=0.2)

    model = RandomForestClassifier()
    model.fit(X_train, Y_train)
    score = model.score(X_test, Y_test)
    print(score)


if __name__ == "__main__":
    train()
