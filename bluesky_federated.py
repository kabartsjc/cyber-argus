
import logging

        
from federated import Federated

import paho.mqtt.client as mqtt

import time
import math
import bluesky as bs
from bluesky.core import Base
from bluesky.network import subscriber
from bluesky.network.client import Client
from bluesky.stack import stack
import requests

from bluesky.network.server import Server
from bluesky.network.discovery import Discovery
from bluesky import net




import os



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
    def __init__(self, scenario: str, name="bluesky-federate", server="http://localhost:8080"):
        super().__init__(name=name,server=server)
        self.bs = None
        self.collector = AircraftInfoCollector()
        self.scenario = scenario


    def advance_to(self,target_time):
        sim = bs.sim

        # Prime: first step will switch INIT->OP if stack/traffic present
        if sim.state == bs.INIT and (bs.traf.ntraf > 0 or len(bs.stack.get_scendata()[0]) > 0):
            sim.step(0.0)
            bs.net.update()  # flush once here too


        # Step in fixed, deterministic chunks you control
        while sim.simt + 1e-9 < target_time:
            dt = min(self.SIMDT, target_time - sim.simt)   # don’t overshoot the grant
            sim.step(dt)
            bs.net.update()
   
    def publish_state(self, fid, t):
        ac = []
        for i, acid in enumerate(bs.traf.id):
            ac.append({
                "id":  str(acid),
                "lat": float(bs.traf.lat[i]),
                "lon": float(bs.traf.lon[i]),
                "alt": float(bs.traf.alt[i]),
                "gs":  float(bs.traf.gs[i]),
                "hdg": float(bs.traf.hdg[i]) if hasattr(bs.traf, 'hdg') else 0.0,
            })
        requests.post(
            f"{self.server}/api/fed/trackstate",
            json={"federateId": fid, "time": t, "tracks": ac},
            timeout=2
        )
    
    def start_network_server(self, host="localhost", port=10301):
        """Expose BlueSky network server so GUI clients can connect."""
        discovery = Discovery(own_id=self.name)                  # create discovery object

        self.netserver = Server(discovery)
        net.server = self.netserver

         #Open the port
        net.open(host=host, port=port)
        logger.info(f"[Federated:{self.name}] BlueSky network server started on {host}:{port}")
        
        
    def run(self, timeout=None):
        logger.info("Starting BlueSky Federated node...")

        bs.init(mode='sim')           # initializes global modules
        

        bs.settings.set_variable_defaults(send_port=12001, recv_port=12000)
        discovery = Discovery(own_id=b"SERVER", is_client=False)
    
        scenario_path = os.path.join(
            os.path.dirname(__file__),   # directory of bluesky_federated.py
            "scenarios",
            self.scenario
        )

        
        bs.stack.stack("IC " + scenario_path)


        fed_id, t = self.register()

        self.netserver = Server(discovery=discovery)

            
        while self.active:
            try:
                t_req = t+ self.MACRO
                t_grant = self.request_time(fed_id, t_req)

                # Step BS up to the granted time
                self.advance_to(t_grant)

                self.publish_state(fed_id, t_grant)


                # >>> IMPORTANT: flush network so server/GUI see updates
                try:
                    bs.net.update()
                except Exception:
                    pass

                t = t_grant


            except requests.exceptions.RequestException as e:
                logging.error(f"[Federated:{self.name}] Request error: {e}. Assuming disconnection or timeout.")
                break