from PIL import Image
import numpy as np
import base64
import io


class Encoder:

    def __init__(self) -> None:
        pass

    @staticmethod
    def encode(data: np.ndarray):

        image = Image.fromarray(data)
        output = io.BytesIO()
        image.save(output, format='JPEG')
        im_data = output.getvalue()
        encoded = base64.b64encode(im_data)

        return encoded


# code for test

if __name__ == "__main__":
    encoder = Encoder()
    decoder = Decoder()
    im = np.array(Image.open('test.jpg'))
    encoded = encoder.encode(im)
    # print(encoded)
    decoded = decoder.decode(encoded)
    gr_im = Image.fromarray(decoded).save('result.jpg')
