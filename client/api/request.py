# from input.DataInstance import DataInstance
# from input.Model import Model

from client.api.encoder import Encoder


class Request:
    encoder = Encoder()

    def __init__(self, model, data_instance):
        self.headers = {"Content-Type": "application/json"}
        self.content = self.prepare(model, data_instance)

    def prepare(self, model, data_instance):

        # not sure how data_instance will look like
        content = {"model": model.config, "data": [{"document_id": 1,
                                                    "pages": [self.encoder.encode(data_instance.data)]}]}

        return content
