from typing import List
from copy import copy

import numpy as np


class DataInstance:
    def __init__(self, images: List[np.ndarray]):
        self._data = images

    @property
    def page_height(self):
        return self.data[0].shape[0]

    @property
    def page_width(self):
        return self.data[0].shape[1]

    @property
    def data(self):
        return copy(self._data)
