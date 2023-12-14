import cv2
from ultralytics import YOLO
import rtsp
import time

from common_utils.web_video_stream_multiple import mjpg_stream
import numpy
from threading import Thread
import os

import paho.mqtt.client as mqtt

YOLO_IA = './yolo/best_ICv2.pt'
IMG_PATH = './img/rtsp_img.jpg'

BROKER_ADDRESS = "smartcampus.maua.br"
BROKER_PORT = 1883
TOPIC = "linguica/ricardo"

class ExtractImage(): 
    def __init__(self, mjpeg_server, rtsp_cameras_transforms):

        self.mjpeg_server = mjpeg_server

        self.rtsp_cameras_transforms = rtsp_cameras_transforms

        self.loops = [True for x in rtsp_cameras_transforms]

        self.threads = []

        self.rtsp_server_uri = [x['rtsp_url'] for x in self.rtsp_cameras_transforms]

 

        for x in range(len(rtsp_cameras_transforms)):

            self.threads.append(Thread(target = self._run, args = [x]))

    def start_threads(self):

        for x in self.threads:

            x.start()

    def _run(self,index):

        try:

            print("Starting Camera#" + str(index+1))

            _image = cv2.VideoCapture(self.rtsp_server_uri[index])
            success, img = _image.read()
            #cv2.imshow("Result", img)
            time.sleep(5)
            cv2.imwrite(IMG_PATH, img)
            while self.loops[index]:

                print('Atualizada Camera#' + str(index+1))

                ret, frame = _image.read()

                if(frame is not None):

                    self.mjpeg_server.update_frame(frame.copy(), index)

                    if cv2.waitKey(1)&0xFF == ord('q'):

                        break
            return _image

 

        except Exception as e:

            print("Error on "+str("Thread#"+str(index+1)))

            print(e)

            ##raise

            print('Ending Camera#' + str(index+1))

    def kill_all(self):

        self.loops = [False for x in self.rtsp_cameras_transforms]

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
    
class Mqtt_sender():
    def __init__(self, address, port, topic, mensagem):
        self.address = address
        self.port = port
        self.topic = topic
        self.mensagem = mensagem
        
    def send_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            print("Connected with result code " + str(rc))  

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
            client.subscribe(self.topic)
        # Publicar a mensagem no tópico especificado após a conexão bem-sucedida
            client.publish(TOPIC, self.mensagem)

        # The callback for when a PUBLISH message is received from the server.
        def on_message(client, userdata, msg):
            print(msg.topic + " " + str(msg.payload))

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(self.address, self.port, 60)

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        client.loop_forever()

def main():
    rtsp_cameras_transforms = [
     {'rtsp_url':'rtsp://admin:SmartCamera@10.33.133.146:554/cam/realmonitor?channel=1&subtype=0',

     'mjpeg_url_ext':'agro_cam'}
    ]
    streams = [x['mjpeg_url_ext'] for x in rtsp_cameras_transforms]
    #mjpg_server = mjpg_stream(ip = '127.0.0.1', streams = streams, port = 8090)
    time.sleep(0.8)
    #rtsp_transform = ExtractImage(mjpg_server, rtsp_cameras_transforms)
    #rtsp_transform.start_threads()

    result_img_with_box = DetectionBox(IMG_PATH)
    measureBox = MeasureBox(result_img_with_box.result)
    img_size = ImgSize(IMG_PATH)
    img_size.img_values(img_size.image)
    
    img_rect = ImgRect(IMG_PATH,measureBox._coordenadas_caixa)
    img_rect.show_img_com_rect()
    rect_values = str(img_rect.rect_values)

    mqtt_sender = Mqtt_sender(BROKER_ADDRESS,BROKER_PORT,TOPIC, rect_values)
    mqtt_sender.send_mqtt()
    
    
if __name__ == "__main__":
    main()