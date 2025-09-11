from bluesky.network.server import Server
from bluesky.network.discovery import Discovery
import bluesky as bs

if __name__ == "__main__":
    bs.settings.set_variable_defaults(send_port=12001, recv_port=12000)
    discovery = Discovery(own_id=b"SERVER", is_client=False)
    server = Server(discovery=discovery)
    server.start()   # run in thread
    server.join()
