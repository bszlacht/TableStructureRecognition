from PIL import Image
import numpy as np
import fitz
import cv2

from .data_instance import DataInstance


class FileReader:

    @staticmethod
    def extension(filename: str):
        return filename.rsplit('.', 1)[-1]

    def _convert_PDF(self, filename: str) -> DataInstance:
        zoom = 2
        mat = fitz.Matrix(zoom, zoom)
        doc = fitz.open(filename)
        imgs = []

        for page in doc:
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            imgs.append(img)

        for i in range(len(imgs)):
            imgs[i] = np.array(imgs[i])
        return DataInstance(imgs)

    def _read_image(self, filename: str) -> np.ndarray:
        return cv2.imread(filename)

    def read(self, *filenames: str) -> DataInstance:
        """Read in the filenames passed and return a corresponding DataInstance object.
        Bear in mind, that all the filenames passed will be counted as one document, so you
        are allowed to pass either one PDF document, or multiple images.
        """

        if not filenames:
            raise ValueError('pass at least one filename')

        ext = self.extension(filenames[0])
        if len(filenames) > 1:
            if not all(map(lambda p: self.extension(p) == ext, filenames)):
                raise ValueError('all the files passed in one call must have the same extension')

            if ext == 'pdf':
                raise ValueError('you cannot pass multiple pdfs at once, only multiple images')

        if ext == 'pdf':
            return self._convert_PDF(filenames[0])

        return DataInstance([self._read_image(filename) for filename in filenames])

   

if __name__ == "__main__":
    fileReader = FileReader("sample.pdf")
    print(fileReader.convert().data)
