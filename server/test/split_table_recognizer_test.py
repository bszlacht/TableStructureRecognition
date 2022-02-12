from server.model import SplitTableModel, SplitTableHeuristic
from server.service import *


def prepare_document():
    cell_1_1 = Cell(BBox(Point2D(0, 9), Point2D(1, 10)), 1)
    cell_1_2 = Cell(BBox(Point2D(1, 9), Point2D(2, 10)), 1)
    cell_1_3 = Cell(BBox(Point2D(2, 9), Point2D(3, 10)), 1)

    cell_2_1 = Cell(BBox(Point2D(0, 0), Point2D(1, 1)), 2)
    cell_2_2 = Cell(BBox(Point2D(1, 0), Point2D(2, 1)), 2)
    cell_2_3 = Cell(BBox(Point2D(2, 0), Point2D(3, 1)), 2)

    row1 = Row()
    row1.add_cell(cell_1_1)
    row1.add_cell(cell_1_2)
    row1.add_cell(cell_1_3)

    row2 = Row()
    row2.add_cell(cell_2_1)
    row2.add_cell(cell_2_2)
    row2.add_cell(cell_2_3)

    table1 = Table(BBox(Point2D(0, 9), Point2D(3, 10)), 1, True)
    table1.add_row(row1)

    table2 = Table(BBox(Point2D(0, 0), Point2D(3, 1)), 2, True)
    table2.add_row(row2)

    document = Document(10, 10, None)
    document.add_table(table1)
    document.add_table(table2)

    return document


def test_split_table_model():
    document = prepare_document()
    model = SplitTableModel()
    result = model.process(document)
    assert len(result.tables) == 1


def test_split_table_heuristics():
    document = prepare_document()
    heuristic = SplitTableHeuristic()
    result = heuristic.process(document)
    assert len(result.tables) == 1


def test_split_table_recognizer():
    test_split_table_model()
    test_split_table_heuristics()


test_split_table_recognizer()
