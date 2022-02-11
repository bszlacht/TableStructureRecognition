from numpy import ndarray
from FileReader.DataInstance import DataInstance
import cv2
from pdf2image import convert_from_path
import numpy
class FileReader:
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.n = len(file_name)

    def convert(self) -> DataInstance:
        if self.file_name.endswith('.pdf'):
            return self._convert_PDF()
        elif self.file_name.endswith(".jpg"):
            return self._convert_JPG()
        else:
            raise Exception("Wrong file extenison")

    def _convert_PDF(self) -> DataInstance:
        imgs = convert_from_path(self.file_name,poppler_path= r"C:\Program Files\poppler-21.11.0\Library\bin")
        for i in range (len(imgs)):
            imgs[i] = numpy.array(imgs[i])
        return DataInstance(imgs)

    def _convert_JPG(self) -> DataInstance:
        img = cv2.imread(self.file_name)
        return DataInstance([img])
