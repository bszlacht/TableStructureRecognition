from typing import List
import requests

import numpy as np

from ..service import Document
from ..controller import Encoder


class OCR:
    SUPPORTED_LANGUAGES = ['en', 'pl', 'uk', 'ru']
    
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port

        self._encoder = Encoder()

    @property
    def ocr_url(self):
        return f'http://{self._host}:{self._port}/recognize'

    def _request(self, images: List[np.ndarray], library: str, lang: List[str]):
        encoded = [self._encoder.encode(image).decode('ascii') for image in images]
        response = requests.post(self.ocr_url, json={
            'images': encoded,
            'lang': lang,
            'library': library
        })

        response = response.json()

        if response['errors']:
            raise RuntimeError(response['errors'][0])

        return response['texts']

    def process(self, document: Document, library: str, lang: List[str]) -> Document:
        library = library.lower()
        if library not in ['tesseract', 'easyocr']:
            raise ValueError('library can be either "Tesseract" or "EasyOCR"')

        if isinstance(lang, str):
            lang = [lang]

        for lang_code in lang:
            if lang_code not in self.SUPPORTED_LANGUAGES:
                raise ValueError('unsupported language, currently only "en", "pl", "uk" and "ru" available')

        cells = []
        images = []
        for table in document.tables:
            padding = 0
            if table.is_borderless:
                padding = 7

            for row in table.rows:
                for cell in row.cells:
                    image = document.pages[cell.page_index]
                    bbox = cell.bbox
                    
                    sub_image = image[bbox.upper_left.y - padding : bbox.lower_right.y + padding,
                                      bbox.upper_left.x - padding : bbox.lower_right.x + padding]

                    cells.append(cell)
                    images.append(sub_image)

        texts = self._request(images, library, lang)

        for text, cell in zip(texts, cells):
            cell.text = text
        
        return document
