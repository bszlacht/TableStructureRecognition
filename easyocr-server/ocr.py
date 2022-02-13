from operator import itemgetter
from typing import List, Tuple, Union
from copy import copy

import numpy as np
import easyocr


class OCR:
    SUPPORTED_LANGUAGES = ['en', 'pl', 'uk', 'ru']

    def __init__(self, lang: Union[str, List[str]] = 'pl') -> None:
        if isinstance(lang, str):
            lang = [lang]

        for lang_code in lang:
            if lang_code not in self.SUPPORTED_LANGUAGES:
                raise ValueError('unsupported language, currently only "en", "pl", "uk" and "ru" available')

        self._lang = lang

        self._reader = easyocr.Reader(lang, 
                                      gpu=True, 
                                      download_enabled=True, 
                                      detector=True, 
                                      recognizer=True)

    @property
    def library(self) -> str:
        return self._library

    @property
    def lang(self) -> List[str]:
        return copy(self._lang)

    # list of tuples (<list of 4 points>, <text string>, <score>)
    def recognize(self, image: np.ndarray) -> Tuple[List[List[int]], str, float]:
        recognized = self._reader.readtext(image)
        
        return max(recognized, key=itemgetter(2))[1]
