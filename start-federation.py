import threading
import time
from federated import Federated

federates = [
    Federated(name="adsb-federate"),
    Federated(name="radar-federate"),
    Federated(name="other-federate")
]

def run_federate(fed):
    fed.run(timeout=5)

threads = []
for fed in federates:
    t = threading.Thread(target=run_federate, args=(fed,), daemon=True)
    t.start()
    threads.append(t)

# Keep main thread alive to let federates run indefinitely
try:
    while any(t.is_alive() for t in threads):
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[Driver] Stopping all federates...")
    for fed in federates:
        fed.stop()
