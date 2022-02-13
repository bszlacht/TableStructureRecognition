from typing import List
import numpy as np


class DataInstance:
    def __init__(self, pic: List[np.ndarray]):
        self.data = pic

