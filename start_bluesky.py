import json
from bluesky_federated import BlueSkyFederated

if __name__ == "__main__":
    # Load configuration from JSON file
    with open("bluesky_sim.json", "r") as f:
        config = json.load(f)

    # Extract params (with defaults if missing)
    scenario = config.get("scenario", "scenarios/demo.scn")
    name = config.get("name", "bluesky-federate")
    server = config.get("server", "http://localhost:8080")
    broker = config.get("broker", "localhost")

    # Create and run federate
    node = BlueSkyFederated(scenario=scenario, name=name, server=server)
    node.run()
