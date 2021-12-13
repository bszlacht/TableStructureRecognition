class Cell:
    def __init__(self, text: str):
        self._text = text

    @property
    def text(self):
        return self._text


class Row:
    def __init__(self):
        self._cells = []

    def add_cell(self, cell: Cell):
        self._cells.append(cell)

    @property
    def cells(self):
        return self._cells


class Table:
    def __init__(self):
        self._rows = []

    def add_row(self, row: Row):
        self._rows.append(row)

    @property
    def rows(self):
        return self._rows


class Document:
    def __init__(self):
        self._tables = []

    def add_table(self, table: Table):
        self._tables.append(table)

    @property
    def tables(self):
        return self._tables
