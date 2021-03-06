from mmdet.apis import init_detector, inference_detector
from mmdet.models.detectors.cascade_rcnn import CascadeRCNN
import numpy as np

from itertools import chain

from ..service import Document, Table, Row, Cell, BBox, Point2D


class NeuralNet:
    CLASSES = ('Bordered', 'cell', 'Borderless')

    def __init__(self, 
                 config_file: str, 
                 checkpoint_file: str = None,
                 device: str = 'cuda:0') -> None:
                 
       self.model: CascadeRCNN = init_detector(str(config_file), str(checkpoint_file), device)

    def predict(self, document: Document, threshold: float = 0.85) -> Document:
        for page_index, page in enumerate(document.pages):
            result = inference_detector(self.model, page)
            result = result[0][:len(self.CLASSES)]

            bordered_tables = []
            borderless_tables = []
            cells = []

            for class_index, detected in enumerate(result):
                for element in detected:
                    # filtering by score
                    if element[4] < threshold:
                        continue

                    upper_left = Point2D(int(element[0]), int(element[1]))
                    lower_right = Point2D(int(element[2]), int(element[3]))

                    bbox = BBox(upper_left, lower_right)

                    if self.CLASSES[class_index] == 'Bordered':
                        table = Table(bbox, page_index, True)
                        bordered_tables.append(table)
                    
                    elif self.CLASSES[class_index] == 'Borderless':
                        table = Table(bbox, page_index, False)
                        borderless_tables.append(table)
                    
                    else:
                        cell = Cell(bbox, page_index)
                        cells.append(cell)

            # assigning cells to borderless tables for future postprocessing
            for cell in cells:
                for table in borderless_tables:
                    if table.bbox.overlaps(cell.bbox):
                        if not table.rows:
                            # thiw row will collect all the detected cells (will be grouped into rows later)
                            table.add_row(Row())
                        table.rows[0].add_cell(cell)

            for table in chain(bordered_tables, borderless_tables):
                document.add_table(table)

        return document
