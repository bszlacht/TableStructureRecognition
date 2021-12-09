class Document:
    def __init__(self):
        self.tables = []

    def add_table(self, table):
        self.tables.append(table)

    def get_tables(self):
        return self.tables


class Table:
    def __init__(self):
        self.rows = []

    def add_row(self, row):
        self.rows.append(row)

    def get_rows(self):
        return self.rows


class Row:
    def __init__(self):
        self.cells = []

    def add_cell(self, cell):
        self.cells.append(cell)

    def get_cells(self):
        return self.cells


class Cell:
    def __init__(self, text):
        self.text = text

    def get_text(self):
        return self.text

