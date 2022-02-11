from __future__ import annotations
from typing import List

import numpy as np


class Point2D:
    def __init__(self, x: int, y: int):
        self._x: int = x
        self._y: int = y

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y


class BBox:
    def __init__(self, upper_left: Point2D, lower_right: Point2D):
        self._upper_left: Point2D = upper_left
        self._lower_right: Point2D = lower_right

    @property
    def upper_left(self) -> Point2D:
        return self._upper_left

    @property
    def lower_right(self) -> Point2D:
        return self._lower_right

    def to_array(self) -> List[int]:
        return [self._upper_left.x, self._upper_left.y, self._lower_right.x, self.lower_right.y]

    def width(self) -> int:
        return self._lower_right.x - self._upper_left.x

    def height(self) -> int:
        return self._lower_right.y - self._upper_left.y

    def intersection(self, bbox: BBox) -> int:
        left = max(self._upper_left.x, bbox.upper_left.x)
        right = min(self._lower_right.x, bbox.lower_right.x)
        top = max(self._upper_left.y, bbox.upper_left.y)
        bottom = min(self._lower_right.y, bbox.lower_right.y)

        if left < right and bottom > top:
            return (right - left) * (bottom - top)
        return 0

    def overlaps(self, bbox: BBox) -> bool:
        return self.upper_left.x <= bbox.lower_right.x and self.upper_left.y <= bbox.lower_right.y \
           and bbox.lower_right.x <= self._upper_left.x and bbox.lower_right.y <= self._upper_left.y

    def area(self) -> int:
        return (self._lower_right.x - self._upper_left.x) * (self._lower_right.y - self._upper_left.y)


class Component:
    def __init__(self):
        self._children: List[Component] = []


class Cell(Component):
    def __init__(self, bbox: BBox, page_index: int):
        super().__init__()
        self._text = ''
        self._bbox = bbox
        self._page_index = page_index

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value

    @property
    def bbox(self) -> BBox:
        return self._bbox

    @property
    def page_index(self) -> int:
        return self._page_index


class Row(Component):
    def add_cell(self, cell: Cell):
        self._children.append(cell)

    @property
    def cells(self) -> List[Cell]:
        return self._children


class Table(Component):
    def __init__(self, bbox: BBox, page_index: int):
        super().__init__()
        self._bbox = bbox
        self._page_index = page_index

    def add_row(self, row: Cell):
        self._children.append(row)

    @property
    def rows(self) -> List[Row]:
        return self._children

    @property
    def bbox(self) -> BBox:
        return self._bbox

    @property
    def page_index(self) -> int:
        return self._page_index


# I assume that document has several pages and each of them has the same width and height
class Document(Component):
    def __init__(self, width: int, height: int, pages: List[np.ndarray]):
        super().__init__()
        self._width = width
        self._height = height
        self._pages = pages

    def add_table(self, table: Component):
        self._children.append(table)

    def remove_table(self, index: int):
        self._children.pop(index)

    @property
    def tables(self) -> List[Table]:
        return self._children

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def pages(self) -> List[np.ndarray]:
        return self._pages
