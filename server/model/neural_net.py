from mmdet.apis import init_detector, inference_detector
from mmdet.models.detectors.cascade_rcnn import CascadeRCNN
import numpy as np


class NeuralNet:
    def __init__(self, config_file: str, checkpoint_file: str = None,
                 device: str = 'cpu') -> None:
       self.model: CascadeRCNN = init_detector(config_file, checkpoint_file, device)

    def predict(self, image: np.ndarray) -> 'something':
        result = inference_detector(self.model, image)
        return result
