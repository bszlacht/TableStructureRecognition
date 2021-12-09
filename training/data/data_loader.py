import json
from cv2 import imread, IMREAD_GRAYSCALE


class DataLoader:
    def __init__(self):
        self.path = "/home/aneta/Pulpit/Studia/dp-proj/proj/training/data/"
        self.training_loaded = 0
        self.test_loaded = 0
        self.val_loaded = 0

    def load_data(self, batch_size, data_type):

        images = [0] * batch_size
        annotations = [0] * batch_size
        idx = 0

        path = self.path + "image_lists/" + data_type + ".txt"

        with open(path) as file:
            for position, line in enumerate(file):
                if position in range(self.training_loaded, self.training_loaded + batch_size):
                    image_name = line.strip()
                    images[idx] = self.load_image(image_name)
                    annotations[idx] = self.load_annotation(image_name)
                    idx += 1

        if data_type == "training":
            self.training_loaded += batch_size
        elif data_type == "test":
            self.test_loaded += batch_size
        elif data_type == "val":
            self.val_loaded += batch_size

        return images, annotations

    def load_image(self, img_name):
        img_file_name = self.path + "images/" + img_name
        return imread(img_file_name, IMREAD_GRAYSCALE)

    def load_annotation(self, img_name):
        img_core_name, rest = img_name.split('_')
        page_number, _ = rest.split('.')
        annotation_file_name = self.path + "annotations/" + img_core_name + "_tables.json"

        with open(annotation_file_name, 'r') as annotation_file:
            annotation_json = json.load(annotation_file)

        page_json = None
        for i in annotation_json:
            if i['pdf_page_index'] == int(page_number):
                page_json = i
                break

        pdf_table_box = page_json['pdf_table_bbox']
        pdf_rows = page_json['rows']
        rows_number = len(pdf_rows)
        rows = [0] * rows_number
        idx = 0
        for entry in pdf_rows:
            rows[idx] = entry['pdf_row_bbox']
            idx += 1
        return [pdf_table_box] + rows


data_loader = DataLoader()
im, an = data_loader.load_data(10, "training")
print(im)
print(an)
im, an = data_loader.load_data(30, "training")
print(im)
print(an)
