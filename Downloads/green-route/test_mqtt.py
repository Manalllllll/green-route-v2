import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connecte au broker MQTT OK")
    client.subscribe("greenroute/camion")

def on_message(client, userdata, msg):
    print("Message recu :", msg.payload.decode())

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
print("En attente de messages...")
client.loop_forever()