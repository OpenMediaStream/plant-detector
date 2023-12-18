'''
------ Insitituto Mauá de Tecnologia - 2023 ------
IC PLANT-DETECTOR 
    - Student: Ricardo Cabral Banci

CODE REFACTOR AND IMPROVEMENT
    - Caio Rabinovich Panes Brunholi
    - Rogerio Cassares Pires
--------------------------------------------------
'''

'''
- TO DO 
    - Implement IC
    - Send MQTT
        - timestamp
        - X,Y,Z, Tag, Color
    - Docker ignore files
    - New Docker image
    - Upload to DockerHub
'''

# IMPORTS ---------------------------------------------------------------------
import paho.mqtt.client as mqtt
import cv2
from ultralytics import YOLO
import rtsp
import time
from common_utils.web_video_stream_multiple import mjpg_stream
import numpy
from threading import Thread
import os

# -----------------------------------------------------------------------------

# VARIABLES -------------------------------------------------------------------
# MQTT
HOST = "smartcampus.maua.br"
PORT = 1883
USER = "PUBLIC"
PASSWORD = "public"
SUB_TOPIC = "cb/test1"
PUB_TOPIC = "cb/test2"

# YOLO 
YOLO_IA = './yolo/best_ICv2.pt'
IMG_PATH = './img/rtsp_img.jpg'

# RTSP
CAMERA_URL = 'rtsp://admin:SmartCamera@10.33.133.146:554/cam/realmonitor?channel=1&subtype=0'
OUTPUT_FILE = './img/savedframe.jpg'
# -----------------------------------------------------------------------------


# FUNCTIONS -------------------------------------------------------------------
# MQTT
def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    mqttc.publish(PUB_TOPIC, "PONG!", 0) # CB debug
    capture_frame()
    execute_image_recognition()
    


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)

# CAMERA
def capture_frame():
   # Open the RTSP stream
    cap = cv2.VideoCapture(CAMERA_URL)

    # Check if the capture is successfully opened
    if not cap.isOpened():
        print("Error: Could not open RTSP stream.")
        return

    try:
        # Read a single frame
        ret, frame = cap.read()
        # Check if the frame is read successfully
        if not ret:
            print("Error: Could not read frame.")
            return

        # # Display the frame
        # cv2.imshow('RTSP Frame', frame)
        # cv2.waitKey(0) # press 'q' while selecting the picture viwer window to continue
        # save frame
        cv2.imwrite(OUTPUT_FILE, frame)

    finally:
        # Release the capture object
        cap.release()
        # Close the OpenCV window
        cv2.destroyAllWindows()

# IC --------------
# Classes
class DetectionBox(): 
    def __init__(self, img_path):
        self.img_path = img_path
        self.image = cv2.imread(img_path)
        self.model = YOLO(YOLO_IA)
        self.result = self.model(self.image, show=False)

class MeasureBox(): 
    def __init__(self, results):
        self.results = results
        self._coordenadas_caixa = self.result()

    def result(self): 
        for r in self.results:
            boxes = r.boxes
            for box in boxes:
                b = box.xyxy[0]  
                x_min, y_min, x_max, y_max = b[:4]
                height = int((y_max - y_min))

        return x_min, y_min, x_max, y_max

class ImgSize():
    def __init__(self, img_path):
        self.img_path = img_path
        self.image = cv2.imread(img_path)
        
        
    def img_values(self, image): 
        if image is not None:
            height, width, channels = image.shape
            print(f"Altura da imagem: {height} pixels")
            print(f"Largura da imagem: {width} pixels")
        else:
            print("Falha ao carregar a imagem.")

class ImgRect():
    def __init__(self, img_path, rect):
        self.img_path = img_path
        self.image = cv2.imread(img_path)
        self.rect = rect
        self.rect_values = self.rect_values()
        
        
    def show_img_com_rect(self):
        x_min, y_min, x_max, y_max = self.rect
        x_min, y_min, x_max, y_max = int(x_min), int(y_min), int(x_max), int(y_max)
        cv2.rectangle(self.image, (x_min, y_min), (x_max, y_max), (0, 0, 255), 3)
        text = "Pimenteira"
        cv2.putText(self.image, text, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("Imagem com Retangulo", self.image)
        cv2.waitKey(0)

    def rect_values(self):
        x_min, y_min, x_max, y_max = self.rect
        x_min, y_min, x_max, y_max = int(x_min), int(y_min), int(x_max), int(y_max)
        rect_values = int(x_min), int(y_min), int(x_max), int(y_max)

        return rect_values

# Functions
def execute_image_recognition():
    result_img_with_box = DetectionBox(IMG_PATH)
    measureBox = MeasureBox(result_img_with_box.result)
    img_size = ImgSize(IMG_PATH)
    img_size.img_values(img_size.image)
    
    img_rect = ImgRect(IMG_PATH,measureBox._coordenadas_caixa)
    img_rect.show_img_com_rect()
    rect_values = str(img_rect.rect_values)
# ------------------
    
# -----------------------------------------------------------------------------



# MAIN ------------------------------------------------------------------------
# MQTT
def main():
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.username_pw_set(USER, PASSWORD)
    mqttc.connect(HOST, PORT, 60)
    mqttc.subscribe(SUB_TOPIC, 0)
    


    mqttc.loop_forever()
    
    
if __name__ == "__main__":
    main()
# -----------------------------------------------------------------------------
