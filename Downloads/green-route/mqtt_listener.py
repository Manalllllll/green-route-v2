import paho.mqtt.client as mqtt
import json
import time

def on_connect(client, userdata, flags, reason_code, properties):
    print("Connecte OK")
    client.subscribe("greenroute/camion")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        parts = payload.split(" ")
        result = {}
        for item in parts:
            kv = item.split(":")
            if len(kv) == 2:
                result[kv[0]] = float(kv[1])
        with open("donnees.json", "w") as f:
            json.dump(result, f)
        print("Sauvegarde :", result)
    except Exception as e:
        print("Erreur :", e)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="listener-gr")
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
print("En attente...")
client.loop_forever()