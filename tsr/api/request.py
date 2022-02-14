from ..input import Model, DataInstance
from .encoder import Encoder


class Request:
    encoder = Encoder()

    def __init__(self, model: Model, data_instance: DataInstance):
        self.headers = {"Content-Type": "application/json"}
        self.content = self.prepare(model, data_instance)

    def prepare(self, model: Model, data_instance: DataInstance):
        pages = []

        for arr in data_instance.data:
            pages.append(self.encoder.encode(arr).decode('ascii'))

        content = {"model": model.config, "data": [{"document_id": 1,
                                                    "pages": pages,
                                                    "page_width": data_instance.page_width,
                                                    "page_height": data_instance.page_height}]}

        return content
