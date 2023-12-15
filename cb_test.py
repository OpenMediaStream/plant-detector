

'''
- TO DO 
    - Implement IC
    - Send MQTT
        - timestamp
        - X,Y,Z, Tag, Color

'''

# IMPORTS ---------------------------------------------------------------------
import paho.mqtt.client as mqtt
# -----------------------------------------------------------------------------

# VARIABLES -------------------------------------------------------------------
# MQTT
HOST = "smartcampus.maua.br"
PORT = 1883
USER = "PUBLIC"
PASSWORD = "public"
SUB_TOPIC = "cb/test1"
PUB_TOPIC = "cb/test2"
# -----------------------------------------------------------------------------


# FUNCTIONS -------------------------------------------------------------------
def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    mqttc.publish(PUB_TOPIC, "PONG!", 0)


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)
# -----------------------------------------------------------------------------



# MAIN ------------------------------------------------------------------------
#MQTT
mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.username_pw_set(USER, PASSWORD)
mqttc.connect(HOST, PORT, 60)
mqttc.subscribe(SUB_TOPIC, 0)

mqttc.loop_forever()
# -----------------------------------------------------------------------------
