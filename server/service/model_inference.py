from server.model.pipeline import CascadeTabNetPipeline
from server.service import Document, Converter


class ModelInference:
    def __init__(self):
        self.pipeline = CascadeTabNetPipeline()

    def predict(self, pages, model_configuration):
        document = Document(-1, -1, pages) # TODO need size of the document
        result = self.pipeline.run(document, model_configuration)
        return Converter.convert_to_json(result)