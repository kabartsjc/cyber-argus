#!/bin/bash

# === Configuration ===
CONF_FILE="mosquitto.conf"
CONTAINER_NAME="mqtt-broker"
IMAGE="eclipse-mosquitto"
PORT=1883

# === Check for configuration file ===
if [ ! -f "$CONF_FILE" ]; then
  echo "❌ Config file '$CONF_FILE' not found in current directory."
  echo "Please create one with at least:"
  echo "  listener $PORT"
  echo "  allow_anonymous true"
  exit 1
fi

# === Run the container ===
echo "🚀 Starting Mosquitto broker on port $PORT..."

docker run -it --rm \
  --name $CONTAINER_NAME \
  -v "$(pwd)/$CONF_FILE:/mosquitto/config/mosquitto.conf" \
  -p $PORT:$PORT \
  $IMAGE
