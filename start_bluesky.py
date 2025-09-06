import json
import sys
from bluesky_federated import BlueSkyFederated
from bluesky import stack

import json
from bluesky_federated import BlueSkyFederated


if __name__ == "__main__":
    node = BlueSkyFederated()
    node.connect_to_bluesky()
    node.run()