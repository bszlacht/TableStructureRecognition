import json

from server.service.data import *


class Converter:

    @staticmethod
    def convert_to_json(document: Document):
        result = {}
        tables = []

        for table in document.tables:
            rows = []
            for row in table.rows:
                cells = []
                for cell in row.cells:
                    cell_entry = {
                        "text": cell.text,
                        "bbox": cell.bbox.to_array()
                    }
                    cells.append(cell_entry)
                row_entry = {
                    "cells": cells
                }
                rows.append(row_entry)
            table_entry = {
                "rows": rows,
                "bbox": table.bbox.to_array()
            }
            tables.append(table_entry)

        result["tables"] = tables

        return json.dumps(result, indent=2)


# code for tests
if __name__ == "__main__":
    cell_1_1 = Cell("text1", BBox(Point2D(0, 0), Point2D(1, 1)))
    cell_1_2 = Cell("text2", BBox(Point2D(1, 0), Point2D(2, 1)))
    cell_1_3 = Cell("text3", BBox(Point2D(2, 0), Point2D(3, 1)))
    cell_2_1 = Cell("text4", BBox(Point2D(0, 1), Point2D(1, 2)))
    cell_2_2 = Cell("text5", BBox(Point2D(1, 1), Point2D(2, 2)))
    cell_2_3 = Cell("text6", BBox(Point2D(2, 1), Point2D(2, 3)))

    row1 = Row()
    row1.add_cell(cell_1_1)
    row1.add_cell(cell_1_2)
    row1.add_cell(cell_1_3)

    row2 = Row()
    row2.add_cell(cell_2_1)
    row2.add_cell(cell_2_2)
    row2.add_cell(cell_2_3)

    table = Table(BBox(Point2D(0, 0), Point2D(2, 3)))
    table.add_row(row1)
    table.add_row(row2)

    document = Document()
    document.add_table(table)

    print(Converter.convert_to_json(document))
