#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Error: No parameter provided!"
    exit 1
fi
ip_address=$1

LOG_DIR="TCU/logs"
LOG_FILE="$LOG_DIR/hawkbit-device-simulator.log"

if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"  # Logs dir creation if doesn't exist
fi
if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"  # Log file cration if doesn't exist
fi

java -jar Permanent/HawkbitClient/hawkbit-device-simulator-0.3.0-SNAPSHOT.jar $ip_address >> "$LOG_FILE" 2>&1 & #Start the Hawkbit device simulator file and print output in hawkbit-device-simulator.log

LOG_FILE1="$LOG_DIR/update-handler.log"
if [ ! -f "$LOG_FILE1" ]; then
    touch "$LOG_FILE1"  # Log file cration if doesn't exist
fi

python3 Permanent/Watchdog/update_handler.py >> "$LOG_FILE1" 2>&1 &

sigterm_handler() {
	python3 OS.py #start the device simulator script
}

trap 'sigterm_handler' SIGTERM

python3 OS.py #start the device simulator script
