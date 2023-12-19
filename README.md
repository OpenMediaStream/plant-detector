# ☘️ PLANT-DETECTOR 
## Description
### Cientific Initiation (IC) that detects the growth of a plant

### It basicly connects to the IP camera using RTSP, analyzes a frame and draws a box with the type of plant identified.
>Currently it only detects `pimenteiras`


</br>
</br>

# 🚀️ Quick Start
> This Quick Start was written using python==3.10.12
### Create a python virtual enviroment using `venv`:
```bash
python -m venv ./
```
### Activate de enviroment:
```bash
# Linux command
. bin/activate

# Windows command
.\venv\Scripts\activate
```
### Install libraries using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```
### Run script:
```bash
python plant-detector-V02.py
```
</br>
</br>

# 💻️ Documentation
## 🐋️ Docker
### The `Dockerfile` include is the responsable for creating the container that will execute the image recognition software
```Dockerfile
# ultranalytics YOLOv8 image
FROM python:3.10.12-slim-bullseye

WORKDIR /app

# copy files to docker
COPY . . 

# Expose container on port 5222
EXPOSE 5222

# Install the cv2 dependencies that are normally present on the local machine, but might be missing in Docker container
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Install requiments
RUN pip install -r requirements.txt

# Execute file
CMD ["python", "plant-detector-V02.py"]

```
### To build the image use the command:
```bash
docker build -t docker_user/plant-detector-v02 .
```
### To run the container
```bash
docker run plant-detector-v02
```
</br>
</br>

## 👨‍💻️ Main Script
### The main script is the `plant-detector-V02.py`
### It receives a MQTT message as a trigger, than connects to a RTSP camera located at the plant, captures a frame, applies the image recognition and sends another MQTT message to a Node-Red server that plots a frame and label over the camera live stream.

</br>

### The Node-Red flow can be viewed on the `flows.json` file