from client.input.data_instance import DataInstance
import cv2
import numpy
import fitz
from PIL import Image


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
        zoom = 2
        mat = fitz.Matrix(zoom, zoom)
        doc = fitz.open(self.file_name)
        imgs = []

        for page in doc:
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            imgs.append(img)

        for i in range(len(imgs)):
            imgs[i] = numpy.array(imgs[i])
        return DataInstance(imgs)

    def _convert_JPG(self) -> DataInstance:
        img = cv2.imread(self.file_name)
        return DataInstance([img])


if __name__ == "__main__":
    fileReader = FileReader("sample.pdf")
    print(fileReader.convert().data)
