import logging

from server.model.pipeline import CascadeTabNetPipeline
from server.service import Document, Converter


logger = logging.getLogger(__name__)


class ModelInference:
    def __init__(self):
        self.pipeline = CascadeTabNetPipeline()

    def predict(self, pages, page_width, page_height, model_configuration):
        logger.info('Wrapping data into custom objects and sending to the pipeline')

        document = Document(page_width, page_height, pages)
        result = self.pipeline.run(document, model_configuration)

        logger.info('Converting results to JSON')

        return Converter.convert_to_json(result)