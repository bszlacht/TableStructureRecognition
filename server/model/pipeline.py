from server.model.split_table_recognizer import SplitTableRecognizer
from ..service import Document
from . import (NeuralNet, 
               OCR, 
               BorderlessTableCellRecognizer,
               BorderedTableCellRecognizer,
               SplitTableRecognizer, 
               SplitTableModel, 
               SplitTableHeuristic)


class CascadeTabNetPipeline:
    def __init__(self) -> None:
        self._neural_net = NeuralNet()
        
        self._bordered_table_cell_recognizer = BorderedTableCellRecognizer()
        self._borderless_table_cell_recognizer = BorderlessTableCellRecognizer()

        self._split_table_recognizer: SplitTableRecognizer = None

        self._ocr: OCR = None

    def configure(self, config: dict) -> dict:
        if config['splitted_table_recognition'] == 'heuristic':
            self._split_table_recognizer = SplitTableHeuristic()
        else:
            self._split_table_recognizer = SplitTableModel()

        self._ocr = OCR(config['ocr'], config['lang'])

    def flush(self):
        self._split_table_recognizer = None
        self._ocr = None

    def predict(self, document: Document, config: dict) -> Document:
        self.configure(config)

        self._neural_net.predict(document, threshold=config['threshold'])

        self._bordered_table_cell_recognizer
        self._borderless_table_cell_recognizer.recognize_borderless(document)

        self._split_table_recognizer.process(document)

        self._ocr.process(document)

        self.flush()

        return document
