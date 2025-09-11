import paho.mqtt.client as mqtt
import requests
import time
import sys
import json

FEDERATE_NAME = sys.argv[1] if len(sys.argv) > 1 else "adsb-federate"
BROKER = "localhost"
TOPIC = f"cosim/{FEDERATE_NAME}"
SERVER = "http://localhost:8080"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

# Register with orchestrator
r = requests.post(f"{SERVER}/cosim/register", params={"name": FEDERATE_NAME})
print(f"Registered: {FEDERATE_NAME}")

last_tick = -1

while True:
    r = requests.get(f"{SERVER}/cosim/tick")
    response = r.json()
    current_tick = response["time"]
    status = response["status"]

    if current_tick != last_tick:
        # Publish state
        payload = {
            "id": FEDERATE_NAME,
            "time": current_tick,
            "msg": f"State update at t={current_tick}"
        }
        client.publish("cosim/atc", json.dumps(payload))
        print(f"[{FEDERATE_NAME}] Published: {payload}")

        # Send ACK immediately, regardless of status
        ack = requests.post(f"{SERVER}/cosim/ack", params={
            "name": FEDERATE_NAME,
            "tick": current_tick
        })
        print(f"[{FEDERATE_NAME}] ACK for tick {current_tick}: {ack.text}")
        last_tick = current_tick
    else:
        print(f"[{FEDERATE_NAME}] Waiting for next tick...")

    time.sleep(1)
