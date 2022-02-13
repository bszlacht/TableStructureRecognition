from FileReader.DataInstance import DataInstance
# from input.Model import Model

from client.api.encoder import Encoder


class Request:
    encoder = Encoder()

    def __init__(self, model: Model, data_instance: DataInstance):
        self.headers = {"Content-Type": "application/json"}
        self.content = self.prepare(model, data_instance)

    def prepare(self, model, data_instance):
        pages = []

        for arr in data_instance.data:
            pages.append(self.encoder.encode(arr))

        content = {"model": model.config, "data": [{"document_id": 1,
                                                    "pages": pages,
                                                    "page_width": len(data_instance.data[0]),
                                                    "page_height": len(data_instance)}]}

        return content
