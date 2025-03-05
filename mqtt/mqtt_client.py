# mqtt/mqtt_client.py
import paho.mqtt.client as mqtt
import json

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPIC = "poultry/sensors"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print("接收到传感器数据:", data)
    # 此处可将数据存入 MongoDB 或进行进一步处理

def start_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    return client

if __name__ == "__main__":
    start_mqtt_client()
    import time
    while True:
        time.sleep(1)
