from mmdet.apis import init_detector, inference_detector, train_detector
from mmdet.datasets import build_dataset, build_dataloader
from mmdet.models.detectors.cascade_rcnn import CascadeRCNN
import mmcv

# Load model
config_file = 'cascade_mask_rcnn_hrnetv2p_w32_20e.py'
cfg = mmcv.Config.fromfile(config_file)
del cfg['model']['type']
model: CascadeRCNN = CascadeRCNN(**cfg['model'])
model = model.to('cuda:0')

cfg = mmcv.Config.fromfile(config_file)

datasets = [build_dataset(cfg.data.train)]

train_detector(model, datasets, cfg)
