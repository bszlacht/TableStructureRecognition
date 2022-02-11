from server.model.split_table_recognizer import SplitTableRecognizer
from ..service import Document
from . import NeuralNet, OCR


class CascadeTabNetPipeline:
    def __init__(self) -> None:
        self._neural_net = NeuralNet()
        
        self._bordered_table_cell_recognizer = BorderedTableCellRecognizer()
        self._borderless_table_cell_recognizer = BorderlessTableCellRecognizer()

        self._split_table_recognizer: SplitTableRecognizer = None  # ??

        self._ocr: OCR = None

    def configure(self, config: dict):
        pass

    def predict(self, document: Document, model_configuration: dict):
        self.configure(model_configuration)

        self._neural_net.predict(document)
