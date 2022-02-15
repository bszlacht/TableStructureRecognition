import json

from .data import *


class Converter:
    
    @staticmethod
    def bbox_to_json(bbox: BBox):
        return {
            "top_left": {
                "x": int(bbox.upper_left.x),
                "y": int(bbox.upper_left.y)
            },
            "bottom_right": {
                "x": int(bbox.lower_right.x),
                "y": int(bbox.lower_right.y)
            }
        }


    @staticmethod
    def convert_to_json(document: Document):
        result = []

        for table in document.tables:

            table_entry = {}

            content = []
            for row in table.rows:
                row_content = []
                for cell in row.cells:
                    row_content.append(cell.text)
                content.append(row_content)

            table_entry["content"] = content

            if isinstance(table.page_index, list):
                table_entry["page"] = [int(idx) for idx in table.page_index]
            else:
                table_entry["page"] = int(table.page_index)

            # TODO decide if we want only BoundingBoxResponse or List[BoundingBoxResponse] - currently first option

            if isinstance(table.bbox, list):
                table_entry["bbox"] = [Converter.bbox_to_json(bbox) for bbox in table.bbox]
            else:
                table_entry["bbox"] = Converter.bbox_to_json(table.bbox)

            cell_bboxs = []
            for row in table.rows:
                single_row_bboxs = []
                for cell in row.cells:
                    single_row_bboxs.append(Converter.bbox_to_json(cell.bbox))
                cell_bboxs.append(single_row_bboxs)

            table_entry["cell_bboxes"] = cell_bboxs

            result.append(table_entry)

        return result


# code for tests
if __name__ == "__main__":
    cell_1_1 = Cell(BBox(Point2D(0, 0), Point2D(1, 1)), 1)
    cell_1_2 = Cell(BBox(Point2D(1, 0), Point2D(2, 1)), 1)
    cell_1_3 = Cell(BBox(Point2D(2, 0), Point2D(3, 1)), 1)
    cell_2_1 = Cell(BBox(Point2D(0, 1), Point2D(1, 2)), 1)
    cell_2_2 = Cell(BBox(Point2D(1, 1), Point2D(2, 2)), 1)
    cell_2_3 = Cell(BBox(Point2D(2, 1), Point2D(3, 2)), 1)

    row1 = Row()
    row1.add_cell(cell_1_1)
    row1.add_cell(cell_1_2)
    row1.add_cell(cell_1_3)

    row2 = Row()
    row2.add_cell(cell_2_1)
    row2.add_cell(cell_2_2)
    row2.add_cell(cell_2_3)

    table = Table(BBox(Point2D(0, 0), Point2D(3, 2)), 1)
    table.add_row(row1)
    table.add_row(row2)

    document = Document(-1, -1,  list(np.zeros((2,2))))
    document.add_table(table)

    print(Converter.convert_to_json(document))
