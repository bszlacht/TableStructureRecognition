# DPTesseract

## Running docker container

### Preparing the environment

To run docker first install `sudo apt install nvidia-container-runtime`

Make sure you have `nvidia-docker2` installed too!

Then edit/create `/etc/docker/daemon.json` with content:

```
{
    "runtimes": {
        "nvidia": {
            "path": "/usr/bin/nvidia-container-runtime",
            "runtimeArgs": []
         } 
    },
    "default-runtime": "nvidia" 
}
```

And restart docker daemon with `sudo systemctl restart docker`

All of this allows docker to use GPU during build time, as it is needed to compile mmdetection library.

Alternatively, you may run all the commands from [Dockerfile](Dockerfile) by yourself, after running a container, because the GPU will be available then.

### Building and running

Firstly, download the model from [here](https://drive.google.com/file/d/1H5d3QWf7el1oKypxhzqYNDsfggZLzUHU/view?usp=sharing) and save it at the path `server/model/models/model.pth`

Server will use port 8444, you can specify another one in the [docker-compose.yml](docker-compose.yml)

Run `docker-compose up` to start all the containers 

### Troubleshooting

Sometimes EasyOCR may have a problem with downloading a model, you may see this in logs. To fix it you simply need to restart docker daemon with `sudo systemctl restart docker`

## Running client

To install a package simply run `pip install .` in the main directory, this will install `tsr` package, which provides all the functionalities you need.

1. Use FileReader class to load document.
2. Read data to DataInstance class using FileReader read method.
3. Construct model using desirable parameters:
    - method for recognizing split tables: "model" or "heuristic"
    - OCR method: "tesseract" or "easyocr"
    - language for OCR: "pl", "en", "uk", "ru"
    - threshold - to determine the level of certainty - float between 0.0 and 1.0
4. Set address for your Docker server (and chosen port)
5. Use Service predict method to get the result.

## Running scripts

We have created some useful scripts for you to try out! You can check how to use them via `python <script>.py -h`.
