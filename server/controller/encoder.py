from PIL import Image
import numpy as np
import base64
import io


class Encoder:

    def encode(self, data: np.ndarray):

        image = Image.fromarray(data)
        output = io.BytesIO()
        image.save(output, format='JPEG')
        im_data = output.getvalue()
        encoded = base64.b64encode(im_data)

        return encoded
