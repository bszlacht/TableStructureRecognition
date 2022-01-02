class Point2D:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y


class BBox:
    def __init__(self, upper_left: Point2D, lower_right: Point2D):
        self._upper_left = upper_left
        self._lower_right = lower_right

    @property
    def upper_left(self):
        return self._upper_left

    @property
    def lower_right(self):
        return self._lower_right

    def to_array(self):
        return [self._upper_left.x, self._upper_left.y, self._lower_right.x, self.lower_right.y]

    def width(self):
        return self._lower_right.x - self._upper_left.x

    def height(self):
        return self._lower_right.y - self._upper_left.y


class Cell:
    def __init__(self, text: str, bbox: BBox):
        self._text = text
        self._bbox = bbox

    @property
    def text(self):
        return self._text

    @property
    def bbox(self):
        return self._bbox


class Row:
    def __init__(self):
        self._cells = []

    def add_cell(self, cell: Cell):
        self._cells.append(cell)

    @property
    def cells(self):
        return self._cells


class Table:
    def __init__(self, bbox: BBox, page_index: int):
        self._rows = []
        self._bbox = bbox
        self._page_index = page_index

    def add_row(self, row: Row):
        self._rows.append(row)

    @property
    def rows(self):
        return self._rows

    @property
    def bbox(self):
        return self._bbox

    @property
    def page_index(self):
        return self._page_index


# I assume that document has several pages and each of them has the same width and height
class Document:
    def __init__(self, width: int, height: int):
        self._tables = []
        self._width = width
        self._height = height

    def add_table(self, table: Table):
        self._tables.append(table)

    def remove_table(self, index: int):
        self._tables.pop(index)

    @property
    def tables(self):
        return self._tables

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height
