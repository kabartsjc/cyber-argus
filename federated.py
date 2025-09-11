from abc import abstractmethod
import requests
import time
import json
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')

class Federated:
    def __init__(self, name,server="http://localhost:8080"):
        self.name = name
        self.server = server
        self.last_tick = -1
        self.SIMDT  = 0.1                      # internal BlueSky integrator step (s)
        self.MACRO  = 1.0                      # how much we try to advance per grant (s)
        self.active = True

    def register(self):
        r = requests.post(f"{self.server}/api/fed/register",
                      json={"name": self.name, "capabilities":["state.publish"], "lookahead": self.SIMDT})
        
        r.raise_for_status()
        data = r.json()

        logging.info(f"[Federated:{self.name}] {data}")

        return data["federateId"], float(data["simStart"])
    

    def request_time (self, fid, t_req):
        r = requests.post(f"{self.server}/api/fed/requestTime",
                      json={"federateId": fid, "requestTime": t_req})
        
        r.raise_for_status()
        
        logging.info(f"[Federated:{self.name}] Grant-time {r.json()['grantTime']}")

        return float(r.json()["grantTime"])
    
    @abstractmethod
    def publish_state(self,fid, t) -> None:
        """public a state of the node"""
        pass    


    @abstractmethod
    def advance_to(self,target_time) -> None:
        """Advance BlueSky with fixed SIMDT ticks up to target_time."""
        pass    
