from server.model.pipeline import CascadeTabNetPipeline
from server.service import Document, Converter


class ModelInference:
    def __init__(self):
        self.pipeline = CascadeTabNetPipeline()

    def predict(self, pages, page_width, page_height, model_configuration):
        document = Document(page_width, page_height, pages)
        result = self.pipeline.run(document, model_configuration)
        return Converter.convert_to_json(result)