
import logging


from federated import Federated
import json

import paho.mqtt.client as mqtt

import time
import math
import bluesky as bs
from bluesky.core import Base
from bluesky.network import subscriber
from bluesky.network.client import Client
from bluesky.stack import stack


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Federated:bluesky-federate")


class AircraftInfoCollector(Base):
    def __init__(self):
        super().__init__()
        self.aircraft = {}

    @subscriber
    def acdata(self, data):
        # Update the internal dictionary with the latest aircraft state data
        self.aircraft.clear()
        for i in range(len(data.id)):
            ac_id = data.id[i].strip()
            self.aircraft[ac_id] = {
                'lat': data.lat[i],
                'lon': data.lon[i],
                'alt': data.alt[i],
                'tas': data.tas[i],
                'gs': data.gs[i],
                'vs': data.vs[i],
                'hdg': data.hdg[i] if hasattr(data, 'hdg') else 0,
                'dest': data.dest[i] if hasattr(data, 'dest') else '',
            }
        

    def get_all_aircraft(self):
        return self.aircraft


class BlueSkyFederated(Federated):

    def __init__(self, name="bluesky-federate", broker="localhost", server="http://localhost:8080"):
        super().__init__(name=name, broker=broker, server=server)
        self.mqtt_client = mqtt.Client(client_id=name)
        self.mqtt_client.connect(broker, 1883, 60)
        self.mqtt_client.loop_start()
        self.bs = None
        self.collector = AircraftInfoCollector()
        self.topic = "cosim/tracks"

    def connect_to_bluesky(self):
        bs.init(mode='client')
        self.bs = Client()
        self.bs.connect()
        logger.info("Connecting to BlueSky...")
    
   
    def update_bluesky_track_list(self):
        aircraft_data = self.collector.get_all_aircraft()
        msg = json.dumps(aircraft_data, indent=4)
        self.mqtt_client.publish(self.topic, msg)
        logger.info(f"Published aircraft: {msg}")

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
                else:
                    logger.info(f"[Update the server to get new information")
                    self.bs.update()

                    self.update_bluesky_track_list()

                    if current_tick != self.last_tick:
                        self.publish(current_tick)
                        self.ack(current_tick)
                        self.last_tick = current_tick
                    else:
                        logging.debug(f"[Federated:{self.name}] Waiting for next tick...")
            
            except requests.exceptions.RequestException as e:
                logging.error(f"[Federated:{self.name}] Request error: {e}. Assuming disconnection or timeout.")
                break