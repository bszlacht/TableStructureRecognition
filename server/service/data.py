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

    def intersection(self, bbox):
        left = max(self._upper_left.x, bbox.upper_left.x)
        right = min(self._lower_right.x, bbox.lower_right.x)
        top = max(self._upper_left.y, bbox.upper_left.y)
        bottom = min(self._lower_right.y, bbox.lower_right.y)

        if left < right and bottom > top:
            return (right - left) * (bottom - top)
        return 0

    def area(self):
        return (self._lower_right.x - self._upper_left.x) * (self._lower_right.y - self._upper_left.y)


class Component:
    def __init__(self):
        self._children = []


class Cell(Component):
    def __init__(self, text: str, bbox: BBox, page_index: int):
        super().__init__()
        self._text = text
        self._bbox = bbox
        self._page_index = page_index

    @property
    def text(self):
        return self._text

    @property
    def bbox(self):
        return self._bbox

    @property
    def page_index(self):
        return self._page_index


class Row(Component):
    def add_cell(self, cell: Component):
        self._children.append(cell)

    @property
    def cells(self):
        return self._children


class Table(Component):
    def __init__(self, bbox: BBox, page_index: int):
        super().__init__()
        self._bbox = bbox
        self._page_index = page_index

    def add_row(self, row: Component):
        self._children.append(row)

    @property
    def rows(self):
        return self._children

    @property
    def bbox(self):
        return self._bbox

    @property
    def page_index(self):
        return self._page_index


# I assume that document has several pages and each of them has the same width and height
class Document(Component):
    def __init__(self, width: int, height: int, pages: list):
        super().__init__()
        self._width = width
        self._height = height
        self._pages = pages

    def add_table(self, table: Component):
        self._children.append(table)

    def remove_table(self, index: int):
        self._children.pop(index)

    @property
    def tables(self):
        return self._children

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def pages(self):
        return self._pages
