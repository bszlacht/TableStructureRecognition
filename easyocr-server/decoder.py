from PIL import Image
import numpy as np

import base64
import io


class Decoder:
    def __init__(self) -> None:
        pass

    def decode(self, data):
        data = data.encode('ascii')
        decoded = base64.decodebytes(data)
        image = Image.open(io.BytesIO(decoded))

        return np.array(image, dtype=np.uint8)
