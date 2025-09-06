import paho.mqtt.client as mqtt
import requests
import time
import json
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')

class Federated:
    def __init__(self, name, broker="localhost", server="http://localhost:8080", topic_prefix="cosim"):
        self.name = name
        self.broker = broker
        self.server = server
        self.topic = f"{topic_prefix}/{self.name}"
        self.client = mqtt.Client()
        self.client.connect(self.broker, 1883, 60)
        self.last_tick = -1
        self.active = True

    def register(self):
        r = requests.post(f"{self.server}/cosim/register", params={"name": self.name})
        logging.info(f"[Federated:{self.name}] {r.text}")

    def run(self, timeout=None):
        self.register()
        while self.active:
            try:
                r = requests.get(f"{self.server}/cosim/tick", timeout=timeout)
                response = r.json()
                current_tick = response["time"]
                status = response["status"]

                if current_tick == -1:
                    logging.info(f"[Federated:{self.name}] Received finalization tick -1. Shutting down.")
                    self.active = False
                    break

                if current_tick != self.last_tick:
                    self.publish(current_tick)
                    self.ack(current_tick)
                    self.last_tick = current_tick
                else:
                    logging.debug(f"[Federated:{self.name}] Waiting for next tick...")

                time.sleep(1)

            except requests.exceptions.RequestException as e:
                logging.error(f"[Federated:{self.name}] Request error: {e}. Assuming disconnection or timeout.")
                break

    def publish(self, tick):
        payload = {
            "id": self.name,
            "time": tick,
            "msg": f"State update at t={tick}"
        }
        self.client.publish("cosim/atc", json.dumps(payload))
        logging.info(f"[Federated:{self.name}] Published: {payload}")

    def ack(self, tick):
        try:
            r = requests.post(f"{self.server}/cosim/ack", params={"name": self.name, "tick": tick})
            logging.info(f"[Federated:{self.name}] ACK for tick {tick}: {r.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"[Federated:{self.name}] ACK error: {e}")

    def stop(self):
        self.active = False