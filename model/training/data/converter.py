import json
from cv2 import imread, IMREAD_GRAYSCALE


class DataConverter:
    def __init__(self):
        self.path = "/home/aneta/Pulpit/Studia/dp-proj/proj/model/training/data/"
        self.training_loaded = 0
        self.test_loaded = 0
        self.val_loaded = 0
        self.images_entries = []
        self.annotations_entries = []

    def convert_data_to_COCO(self):

        path = self.path + "image_lists/" + "images_list.txt"
        ann_id = 1
        img_id = 1

        with open(path) as file:
            for position, line in enumerate(file):
                image_name = line.strip()
                img = self.load_image(image_name)

                im_entry = {
                    'file_name': image_name,
                    'height': img.shape[0],
                    'width': img.shape[1],
                    'id': img_id
                }

                self.images_entries.append(im_entry)

                ann_id = self.load_annotation(image_name, img.shape, ann_id, img_id)
                img_id += 1

                if img_id % 1000 == 0:
                    print(img_id)

        json_en = {
            "images": self.images_entries,
            "annotations": self.annotations_entries,
            "categories": [
                {
                    "id": 1,
                    "name": "table",
                    "supercategory": "none"
                },
                {
                    "id": 2,
                    "name": "cell",
                    "supercategory": "none"
                }
            ]
        }
        json_obj = json.dumps(json_en, indent=2)
        with open("coco.json", "w") as outfile:
            outfile.write(json_obj)

    def load_image(self, img_name: str):
        img_file_name = self.path + "images/" + img_name
        return imread(img_file_name, IMREAD_GRAYSCALE)

    def area(self, bbox):
        return (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])

    def segmentation(self, bbox):
        return [bbox[0], bbox[1], bbox[0], bbox[3], bbox[2], bbox[3], bbox[2], bbox[1]]

    def load_annotation(self, img_name, img_shape, ann_id, img_id):
        img_core_name, rest = img_name.split('_')
        page_number, _ = rest.split('.')
        annotation_file_name = self.path + "annotations/" + img_core_name + "_tables.json"

        with open(annotation_file_name, 'r') as annotation_file:
            annotation_json = json.load(annotation_file)

        page_json = []
        for i in annotation_json:
            if i['pdf_page_index'] == int(page_number):
                page_json.append(i)

        for p_j in page_json:
            _, _, y_max, x_max = p_j['pdf_full_page_bbox']
            scale_x = img_shape[0] / x_max
            scale_y = img_shape[1] / y_max

            pdf_table_box = p_j['pdf_table_bbox']
            pdf_table_box[0] *= scale_x
            pdf_table_box[2] *= scale_x
            pdf_table_box[1] *= scale_y
            pdf_table_box[3] *= scale_y

            for i in range(4):
                pdf_table_box[i] = int(pdf_table_box[i])

            cells = p_j['cells']
            for entry in cells:
                cell_bbox = entry['pdf_bbox']
                cell_bbox[0] *= scale_x
                cell_bbox[2] *= scale_x
                cell_bbox[1] *= scale_y
                cell_bbox[3] *= scale_y

                for i in range(4):
                    cell_bbox[i] = int(cell_bbox[i])

                cell_annot = {
                    "area": self.area(cell_bbox),
                    "bbox": cell_bbox,
                    "category_id": 2,
                    "id": ann_id,
                    "ignore": 0,
                    "image_id": img_id,
                    "iscrowd": 0,
                    "segmentation": self.segmentation(cell_bbox)
                }
                self.annotations_entries.append(cell_annot)
                ann_id += 1

            annot = {
                "area": self.area(pdf_table_box),
                "bbox": pdf_table_box,
                "category_id": 1,
                "id": ann_id,
                "ignore": 0,
                "image_id": img_id,
                "iscrowd": 0,
                "segmentation": self.segmentation(pdf_table_box)
            }
            self.annotations_entries.append(annot)
            ann_id += 1

        return ann_id


data_converter = DataConverter()
data_converter.convert_data_to_COCO()
