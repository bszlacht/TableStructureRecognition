import pytest

from server.model import OCR
from server.service import Document, Cell, Point2D, BBox, Row, Table
import cv2


def prepare_document():
    img = cv2.imread("demo.jpg")
    document = Document(136, 76, img)
    cell_1_1 = Cell(BBox(Point2D(6, 5), Point2D(74, 23)), 1)
    cell_1_2 = Cell(BBox(Point2D(74, 5), Point2D(129, 23)), 1)
    row = Row()
    row.add_cell(cell_1_1)
    row.add_cell(cell_1_2)
    table = Table(BBox(Point2D(6, 5), Point2D(129, 23)), 1, True)
    document.add_table(table)
    return document


def test_tesseract():
    ocr = OCR("tesseract", "en")
    document = prepare_document()

    cells = ocr.process(document).tables[0].rows[0].cells
    for cell in cells:
        assert cell.text != ''


def test_easy_ocr():
    ocr = OCR("easyocr", "en")
    document = prepare_document()

    cells = ocr.process(document).tables[0].rows[0].cells
    for cell in cells:
        assert cell.text != ''


def test_ocr():
    test_tesseract()
    test_easy_ocr()


test_ocr()
