from argparse import ArgumentParser
from itertools import chain

import cv2

from tsr import Service, FileReader, ModelDirector


def visualize_bbox(image, bbox, rgb=(0, 0, 255)):
    tl = bbox['top_left']
    br = bbox['bottom_right']
    return cv2.rectangle(image, (tl['x'], tl['y']), (br['x'], br['y']), rgb, 2)


if __name__ == "__main__":
    parser = ArgumentParser()
    
    parser.add_argument('filenames', nargs='+', help='filenames to process')
    parser.add_argument('--split_table', default='model', help='the way to process splitted tables (model|heuristic)')
    parser.add_argument('--library', default='easyocr', help='a library for the ocr (easyocr|tesseract)')
    parser.add_argument('--lang', default='en', help='language of the document (en|pl|ru|uk)')
    parser.add_argument('--threshold', type=float, default=0.85, help='threshold score for the output of the model')
    parser.add_argument('--address', default='127.0.0.1:8444', help='address of the server')

    args = parser.parse_args()

    file_reader = FileReader()
    data_instance = file_reader.read(*args.filenames)
    model = ModelDirector.construct(args.split_table, args.library, args.lang, args.threshold)

    service = Service(args.address)
    response = service.predict(model, data_instance)

    if response['tables']:
        pages = data_instance.data
        for table in response['tables']:
            image = pages[table['page']]
            image = visualize_bbox(image, table['bbox'], rgb=(255, 0, 0))
            for cell_bbox in chain(*table['cell_bboxs']):
                image = visualize_bbox(image, cell_bbox, rgb=(0, 0, 255))

        cv2.imshow('detected elements', image)
        
        while True:
            k = cv2.waitKey(1) & 0xff
            if k == 27: break
    else:
        print('No tables detected')
