from itertools import chain
import json

import cv2


def visualize_bbox(image, bbox, rgb=(0, 0, 255)):
    tl = bbox['top_left']
    br = bbox['bottom_right']
    return cv2.rectangle(image, (tl['x'], tl['y']), (br['x'], br['y']), rgb, 2)


if __name__ == '__main__':
    image = cv2.imread('demo.png')
    with open('respond.json', 'r', encoding='utf-8') as f:
        respond = json.load(f)

    for table in respond['tables']:
        image = visualize_bbox(image, table['bbox'], rgb=(255, 0, 0))
        for cell_bbox in chain(*table['cell_bboxs']):
            image = visualize_bbox(image, cell_bbox, rgb=(0, 0, 255))

    cv2.imshow('detected elements', image)
    
    while True:
        k = cv2.waitKey(1) & 0xff
        if k == 27: break
