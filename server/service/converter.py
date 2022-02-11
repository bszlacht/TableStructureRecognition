import json

# from .data import *
from server.service import *


class Converter:

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

            table_entry["page"] = table.page_index  # TODO maybe change this property to contain multiple page indexes?

            # TODO decide if we want only BoundingBoxResponse or List[BoundingBoxResponse] - currently first option

            table_entry["bbox"] = {
                "top_left": {
                    "x": table.bbox.upper_left.x,
                    "y": table.bbox.upper_left.y
                },
                "bottom_right": {
                    "x": table.bbox.lower_right.x,
                    "y": table.bbox.lower_right.y
                }
            }

            cell_bboxs = []
            for row in table.rows:
                single_row_bboxs = []
                for cell in row.cells:
                    single_row_bboxs.append({
                        "top_left": {
                            "x": cell.bbox.upper_left.x,
                            "y": cell.bbox.upper_left.y
                        },
                        "bottom_right": {
                            "x": cell.bbox.lower_right.x,
                            "y": cell.bbox.lower_right.y
                        }
                    })
                cell_bboxs.append(single_row_bboxs)

            table_entry["cell_bboxs"] = cell_bboxs

            result.append(table_entry)

        return json.dumps(result, indent=2)


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
