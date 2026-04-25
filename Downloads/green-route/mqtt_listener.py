import paho.mqtt.client as mqtt
import json
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config import INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET

# Connexion InfluxDB
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

def on_connect(client, userdata, flags, reason_code, properties):
    print("Connecte MQTT OK")
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

        # Sauvegarde JSON local
        with open("donnees.json", "w") as f:
            json.dump(result, f)

        # Envoi vers InfluxDB
        point = Point("camion") \
            .field("vitesse",    result.get("vitesse", 0)) \
            .field("co2",        result.get("co2", 0)) \
            .field("carburant",  result.get("carburant", 0)) \
            .field("stop",       result.get("stop", 0))

        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        print("Sauvegarde + InfluxDB OK :", result)

    except Exception as e:
        print("Erreur :", e)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="listener-gr")
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
print("En attente des données...")
client.loop_forever()