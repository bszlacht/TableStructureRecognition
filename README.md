# DPTesseract

## Running docker container

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

To build an image use `docker build -t table-structure-recognition .`

To run a container use `docker run -p <your port>:8444 --gpus all --shm-size 6G table-structure-recognition`
