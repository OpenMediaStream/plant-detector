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
