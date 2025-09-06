import json
import time
import logging


import matplotlib
matplotlib.use("Agg")

from bluesky import stack as bs
from bluesky.network.client import Client

from federated import Federated

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Federated:bluesky-federate")


class AircraftCollector:
    """Receives aircraft updates from BlueSky and republishes to MQTT."""
    def __init__(self, mqtt_client, topic="cosim/tracks"):
        self.mqtt_client = mqtt_client
        self.topic = topic

    def __call__(self, topic, payload):
        try:
            data = json.loads(payload)
            # Normalize to list
            rows = data if isinstance(data, list) else [data]
            for ac in rows:
                msg = {
                    "id": ac.get("id") or ac.get("acid") or ac.get("callsign"),
                    "lat": ac.get("lat"),
                    "lon": ac.get("lon"),
                    "alt": ac.get("alt"),
                    "spd": ac.get("spd") or ac.get("tas") or ac.get("gs"),
                    "hdg": ac.get("hdg") or ac.get("trk"),
                }
                self.mqtt_client.publish(self.topic, json.dumps(msg))
                logger.info(f"Published aircraft: {msg}")
        except Exception as e:
            logger.error(f"Error processing aircraft data: {e}")


class BlueSkyFederated(Federated):
    
    def __init__(self, name="bluesky-federate", broker="localhost", server="http://localhost:8080"):
        super().__init__(name=name, broker=broker, server=server)
        self.mqtt_client = mqtt.Client(client_id=name)
        self.mqtt_client.connect(broker, 1883, 60)
        self.mqtt_client.loop_start()
        self.bs = None
        self.collector = AircraftInfoCollector()
        self.topic = "cosim/tracks"
    
    
    
    def __init__(self, name="bluesky-federate", broker="localhost", server="http://localhost:8080"):
        # Base Federated creates MQTT client as self.client
        super().__init__(name=name, broker=broker, server=server)  # :contentReference[oaicite:4]{index=4}
        self.bs = None
        self.collector = AircraftCollector(self.client)  # publish via MQTT

    def connect_to_bluesky(self, scenario=None):
        logger.info("Connecting to BlueSky...")
        bs.init(mode='client')
        self.bs = Client()
        self.bs.connect()

        if scenario:
            logger.info(f"Loading scenario: {scenario}")
            bs.stack(f"SCENARIO {scenario}")
            bs.stack("RUN")   # ensure it starts running
            bs.stack("LIST")   # prints all active aircraft into the BlueSky log


        # Subscribe to AIRCRAFT updates
        aircraft_subscription = self.bs.subscribe("AIRCRAFT", actonly=True)
        aircraft_subscription.connect(self.collector)

        logger.info("Connected and subscribed to BlueSky topic 'AIRCRAFT'.")
    
    
    def run(self, timeout=None):
        logger.info("Starting BlueSky Federated node...")
        self.connect_to_bluesky()

        # Inline copy of Federated.run() so we can pump BlueSky client updates each tick. :contentReference[oaicite:5]{index=5}
        self.register()
        while self.active:
            try:
                import requests
                r = requests.get(f"{self.server}/cosim/tick", timeout=timeout)
                response = r.json()
                current_tick = response["time"]

                if current_tick == -1:
                    logger.info(f"[Federated:{self.name}] Received finalization tick -1. Shutting down.")
                    self.active = False
                    break

                # Pump BlueSky network client so topic handlers fire. :contentReference[oaicite:6]{index=6}
                # Doing it a few times helps drain bursts.
                for _ in range(3):
                    self.bs.update()

                if current_tick != self.last_tick:
                    self.publish(current_tick)
                    self.ack(current_tick)
                    self.last_tick = current_tick
                else:
                    logging.debug(f"[Federated:{self.name}] Waiting for next tick...")

                time.sleep(0.2)

            except requests.exceptions.RequestException as e:
                logging.error(f"[Federated:{self.name}] Request error: {e}. Assuming disconnection or timeout.")
                break

