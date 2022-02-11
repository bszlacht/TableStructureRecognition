from pathlib import Path
import logging

from ..service import Document
from . import (NeuralNet, 
               OCR, 
               BorderlessTableCellRecognizer,
               BorderedTableCellRecognizer,
               SplitTableRecognizer, 
               SplitTableModel, 
               SplitTableHeuristic)


logger = logging.getLogger(__name__)


class CascadeTabNetPipeline:
    def __init__(self) -> None:
        self._model_package_path = Path(__file__).parent

        self._neural_net = NeuralNet(
            self._model_package_path / 'config' / 'cascade_config.py',
            self._model_package_path / 'models' / 'epoch_36.pth'
        )
        
        self._bordered_table_cell_recognizer = BorderedTableCellRecognizer()
        self._borderless_table_cell_recognizer = BorderlessTableCellRecognizer()

        self._split_table_recognizer: SplitTableRecognizer = None

        self._ocr: OCR = None

    def configure(self, config: dict) -> dict:
        if config['splitted_table_recognition'] == 'heuristic':
            self._split_table_recognizer = SplitTableHeuristic()
        else:
            self._split_table_recognizer = SplitTableModel(self._model_package_path / 'models' / 'model.sav')

        self._ocr = OCR(config['ocr'], config['lang'])

    def flush(self):
        self._split_table_recognizer = None
        self._ocr = None

    def run(self, document: Document, config: dict) -> Document:
        logger.info('Configuring models')        
        self.configure(config)

        logger.info('Predicting using a neural net')
        document = self._neural_net.predict(document, threshold=config['threshold'])

        logger.info('Applying postprocessing')
        document = self._bordered_table_cell_recognizer.recognize(document)
        document = self._borderless_table_cell_recognizer.recognize(document)

        logger.info('Trying to join splitted tables')
        document = self._split_table_recognizer.process(document)

        logger.info('Filling in the tables with recognized text')
        document = self._ocr.process(document)

        self.flush()

        return document
