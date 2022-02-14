FROM pytorch/pytorch:1.4-cuda10.1-cudnn7-devel


RUN apt-get update && \
    apt-get install -y less nano htop unzip gcc ffmpeg libsm6 libxext6 git ninja-build libglib2.0-0 libsm6 libxrender-dev libxext6

RUN pip install -q mmcv terminaltables --no-cache-dir
RUN git clone --branch v1.2.0 'https://github.com/open-mmlab/mmdetection.git'


WORKDIR /workspace/mmdetection

RUN pip install -r "requirements/optional.txt" --no-cache-dir
RUN python setup.py install
RUN python setup.py develop
RUN pip install -r "requirements.txt" --no-cache-dir
RUN pip install pillow==6.2.2 gdown pycocotools mmcv==0.4.3 uvicorn==0.17.0 --no-cache-dir

WORKDIR /workspace


COPY server /workspace/server
COPY setup.py /workspace/setup.py

RUN pip install --upgrade pip 

RUN pip install -e . 

WORKDIR /workspace/server/controller
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8444"]
