from operator import itemgetter
from typing import List, Tuple
from copy import copy

import numpy as np
import pytesseract
from pytesseract.pytesseract import SUPPORTED_FORMATS


class OCR:
    SUPPORTED_LANGUAGES = ['en', 'pl', 'uk', 'ru']

    def __init__(self, library: str, lang: str | List[str] = 'pl') -> None:
        self._library = library.lower()
        if self._library not in ['tesseract', 'easyocr']:
            raise ValueError('library can be either "Tesseract" or "EasyOCR"')

        if isinstance(lang, str):
            lang = [lang]

        for lang_code in lang:
            if lang_code not in self.SUPPORTED_LANGUAGES:
                raise ValueError('unsupported language, currently only "en", "pl", "uk" and "ru" available')

        self._lang = lang

        if self._library == 'easyocr':
            import easyocr

            # TODO check if there will be enough RAM/VRAM for all the models
            self._reader = easyocr.Reader(lang, 
                                          gpu=True, 
                                          download_enable=True, 
                                          detector=True, 
                                          recognizer=True)

        elif self._library == 'tesseract':
            import pytesseract

            lang_code_map = {
                'en': 'eng',
                'pl': 'pol',
                'uk': 'ukr',
                'ru': 'rus'
            }

            self._lang = [lang_code_map[lang_code] for lang_code in self._lang]

    @property
    def library(self) -> str:
        return self._library

    @property
    def lang(self) -> List[str]:
        return copy(self._lang)

    # list of tuples (<list of 4 points>, <text string>, <score>)
    def recognize(self, image: np.ndarray) -> List[Tuple[List[List[int]], str, float]]:
        if self.library == 'easyocr':
            recognized = self._reader.readtext(image)
        elif self.library == 'tesseract':
            result = pytesseract.image_to_data(image, lang='+'.join(self.lang))
            valid_idxs = [i for i in range(result['text'])\
                          if result['text'][i] and result['conf'] != '-1']
            
            recognized = []
            for idx in valid_idxs:
                t, l, h, w = (result['top'][idx],
                              result['left'][idx],
                              result['height'][idx],
                              result['width'][idx])

                points = [
                    [l,     t],
                    [l + w, t],
                    [l + w, t + h],
                    [l,     t + h]
                ]

                recognized.append((points, result['text'][idx], points['conf'][idx]))
        else:
            raise TypeError('unknown OCR library set. Must be either "Tesseract" or "EasyOCR"')

        return recognized

    def process(self, document: Document) -> Document:
        for table in document.tables:
            for row in table.rows:
                for cell in table.cells:
                    image = table.pages[cell.page]
                    bbox = cell.bbox
                    
                    sub_image = image[bbox.upper_left.y:bbox.lower_right.y,
                                      bbox.upper_left.x:bbox.lower_right.x]

                    recognized = self.recognize(sub_image)

                    max_score = max(recognized, key=itemgetter(2))
                    max_score_idx = [i for i, (_, _, score) in enumerate(recognized) if score == max_score][0]

                    cell._text = recognized[max_score_idx][1]
        
        return document
