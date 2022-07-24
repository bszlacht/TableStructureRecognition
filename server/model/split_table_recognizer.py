import pickle

from server.service.data import *


class SplitTableRecognizer:

    def process(self, document: Document) -> Document:
        raise NotImplementedError()

    def merge(self, table1: Table, table2: Table) -> Table:
        for row in table2.rows:
            table1.add_row(row)

        table1.add_page_indices(table2.page_index)
        table1.add_bboxes(table2.bbox)

        return table1

    def column_number_diff(self, table1, table2):
        cells1 = table1.rows[-1].cells
        cells2 = table2.rows[0].cells
        return len(cells2) - len(cells1)


class SplitTableModel(SplitTableRecognizer):
    
    def __init__(self, model_path: str) -> None:
        super().__init__()

        self._model = pickle.load(open(model_path, 'rb'))

    def process(self, document: Document) -> Document:

        for i, table1 in enumerate(document.tables):
            for j, table2 in enumerate(document.tables):
                if i == j:
                    continue

                if table2.page_index - table1.page_index != 1:
                    continue

                if self.column_number_diff(table1, table2) != 0:
                    continue

                X = self.calculate_x(document, table1, table2)

                if self.predict(X):
                    document.tables[i] = self.merge(table1, table2)
                    document.remove_table(j)

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
        result = self._model.predict(X)
        return result[0]


class SplitTableHeuristic(SplitTableRecognizer):

    def __init__(self, eps: float = None, margin: float = None):
        self._eps = eps
        self._margin = margin

    def process(self, document: Document) -> Document:

        if not self._eps:
            self._eps = 0.03 * document.tables[0].bbox.width()

        if not self._margin:
            self._margin = 0.12 * document.height

        for i, table1 in enumerate(document.tables):
            for j, table2 in enumerate(document.tables):
                if i == j:
                    continue

                if self.check_merge(table1, table2, document.height):
                    document.tables[i] = self.merge(table1, table2)
                    document.remove_table(j)

            return document

    def check_merge(self, table1: Table, table2: Table, page_height: int) -> bool:

        if table2.page_index - table1.page_index != 1:
            return False

        if self.column_number_diff(table1, table2) != 0:
            return False

        table1_lower_margin = page_height - table1.bbox.lower_right.y
        table2_upper_margin = table2.bbox.upper_left.y

        if table1_lower_margin > self._margin and table2_upper_margin > self._margin:
            return False

        cells1 = table1.rows[-1].cells
        cells2 = table2.rows[0].cells

        for i in range(len(cells1)):
            width1 = cells1[i].bbox.width()
            width2 = cells2[i].bbox.width()
            if abs(width2 - width1) > self._eps:
                return False

        return True
