import pickle

from server.service.data.data import *


class SplitTableRecognizer:
    def process(self, document: Document) -> Document:
        pass

    def merge(self, table1: Table, table2: Table) -> Table:
        for row in table2.rows:
            table1.add_row(row)

        return table1

    def column_number_diff(self, table1, table2):
        cells1 = table1.rows[0].cells
        cells2 = table2.rows[0].cells
        return len(cells2) - len(cells1)


class SplitTableModel(SplitTableRecognizer):

    def process(self, document: Document) -> Document:

        for i in range(len(document.tables) - 1):
            table1 = document.tables[i]
            table2 = document.tables[i + 1]

            if table2.page_index - table1.page_index != 1:
                continue

            if self.column_number_diff(table1, table2) != 0:
                continue

            X = self.calculate_x(document, table1, table2)

            if self.predict(X):
                document.tables[i + 1] = self.merge(table1, table2)
                document.remove_table(i)

        return document

    def calculate_x(self, document, table1, table2):
        return [[
            (document.height - table1.bbox.lower_right.y) / table1.bbox.height(),
            table2.bbox.upper_left.y / table2.bbox.height(),
            abs(table1.bbox.width() - table2.bbox.width()) / table1.bbox.width(),
            abs(table1.bbox.upper_left.x - table2.bbox.upper_left.x) / table1.bbox.width(),
            abs(table1.bbox.lower_right.x - table2.bbox.lower_right.x) / table1.bbox.width()
        ]]

    def predict(self, X: list) -> bool:
        model = pickle.load(open("model.sav", 'rb'))
        result = model.predict(X)
        return result[0]


class SplitTableHeuristic(SplitTableRecognizer):

    def process(self, document: Document) -> Document:

        for i in range(len(document.tables) - 1):
            table1 = document.tables[i]
            table2 = document.tables[i + 1]
            if self.check_merge(table1, table2, document.height):
                document.tables[i + 1] = self.merge(table1, table2)
                document.remove_table(i)

        return document

    def check_merge(self, table1: Table, table2: Table, page_height: int) -> bool:

        eps = 0.05 * table1.bbox.width()
        margin = 0.08 * table1.bbox.height()

        if table2.page_index - table1.page_index != 1:
            return False

        if self.column_number_diff(table1, table2) != 0:
            return False

        table1_lower_margin = page_height - table1.bbox.lower_right.y
        table2_upper_margin = table2.bbox.upper_left.y

        if table1_lower_margin > margin and table2_upper_margin > margin:
            return False

        cells1 = table1.rows[0].cells
        cells2 = table2.rows[0].cells

        for i in range(len(cells1)):
            width1 = cells1[i].bbox.width()
            width2 = cells2[i].bbox.width()
            if abs(width2 - width1) > eps:
                return False

        return True


if __name__ == "__main__":
    cell_1_1 = Cell("text1", BBox(Point2D(0, 9), Point2D(1, 10)), 1)
    cell_1_2 = Cell("text2", BBox(Point2D(1, 9), Point2D(2, 10)), 1)
    cell_1_3 = Cell("text3", BBox(Point2D(2, 9), Point2D(3, 10)), 1)

    cell_2_1 = Cell("text4", BBox(Point2D(0, 0), Point2D(1, 1)), 2)
    cell_2_2 = Cell("text5", BBox(Point2D(1, 0), Point2D(2, 1)), 2)
    cell_2_3 = Cell("text6", BBox(Point2D(2, 0), Point2D(3, 1)), 2)

    row1 = Row()
    row1.add_cell(cell_1_1)
    row1.add_cell(cell_1_2)
    row1.add_cell(cell_1_3)

    row2 = Row()
    row2.add_cell(cell_2_1)
    row2.add_cell(cell_2_2)
    row2.add_cell(cell_2_3)

    table1 = Table(BBox(Point2D(0, 9), Point2D(3, 10)), 1)
    table1.add_row(row1)

    table2 = Table(BBox(Point2D(0, 0), Point2D(3, 1)), 2)
    table2.add_row(row2)

    document = Document(10, 10, [[], []])
    document.add_table(table1)
    document.add_table(table2)

    heuristic = SplitTableModel()
    merged = heuristic.process(document)
    print(len(merged.tables))
