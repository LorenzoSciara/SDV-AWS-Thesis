import time
import threading
import sys
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time
import subprocess
import os
import signal
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

from TCU import subsystems

certificate_path="./Permanent/Certificates/"

def telemetry_handler(): #Function that manage the telemetry data sending to IoTCore via mqtt protocol
    global mqttc
    global connection_event
    #Thing connection
    VIN = "HawkbitDevice001"  ##This is your Thing name
    ENDPOINT = "a1tbrylx7y3p3t-ats.iot.eu-west-1.amazonaws.com"
    CERT_FILEPATH = f"{certificate_path}{VIN}.cert.pem"
    PRIVATE_KEY_FILEPATH = f"{certificate_path}{VIN}.private.key"
    ROOT_CA_FILEPATH = f"{certificate_path}root-CA.crt"
    mqttc = AWSIoTMQTTClient(VIN)
    # Make sure you use the correct region!
    mqttc.configureEndpoint(ENDPOINT, 8883)
    mqttc.configureCredentials(ROOT_CA_FILEPATH, PRIVATE_KEY_FILEPATH, CERT_FILEPATH)
    # Connect to the gateway
    if mqttc.connect():
        print("Connected to IoT core. Now the device sends its telemetry every 1 seconds")
        connection_event.set() #Send connected signal to the main
        publish_topic = f"device/{VIN}/telemetry"
        values = {}
        t = 0
        while True:
            manifest_path = "./TCU/manifest.xml"
            project_type = get_project_type(manifest_path)

            if project_type == "c":
                file_path = "./TCU/main.exe"
                subprocess.run(["chmod", "+x", file_path], check=True)
                launch_project(file_path)
                break
            else:
                print("Impossibile determinare il tipo di progetto.")
            for sub in subsystems:
                values[sub.get_name()] = sub.get_info(t)
            values["Timestamp"] = datetime.isoformat(datetime.utcnow())
            values["DeviceID"] = f"{VIN}"
            print(values)
            messageFinal=json.dumps(values)
            mqttc.publish(publish_topic, messageFinal, 0)
            t = t +1
            print("\n\n\n")
            time.sleep(1)
        interupt_handler()
    else:
    	print("Connection error with IoT Core server!")

def interupt_handler():
    global mqttc
    mqttc.disconnect()
    print("\nDisconcted to IoT core.")
    print("The vehicle is shutting down.")
    
    process = subprocess.Popen(["pgrep", "-f", "update_handler.py"], stdout=subprocess.PIPE, text=True)
    output, _ = process.communicate()
    pid_to_kill_list = output.splitlines()
    for pid_to_kill in pid_to_kill_list:
        print(f"Pid to kill: {pid_to_kill}")
        os.kill(int(pid_to_kill), 9) #Kill the process
        
    print("The update handler process is killed.")
    process = subprocess.Popen(["pgrep", "-f", "hawkbit-device-simulator-0.3.0-SNAPSHOT.jar"], stdout=subprocess.PIPE, text=True)
    output, _ = process.communicate()
    pid_to_kill_list = output.splitlines()
    for pid_to_kill in pid_to_kill_list:
        print(f"Pid to kill: {pid_to_kill}")
        os.kill(int(pid_to_kill), 9) #Kill the process
    print("The hawkbit device simulator process is killed.")
    sys.exit(0)
	
def sigterm_handler(signum, frame):
    global mqttc
    mqttc.disconnect()
    print("\nDisconcted to IoT core.")
    print("The vehicle is shutting down.")
    sys.exit(0)

def print_car():
    print("       _______")
    print("   ___//_____\\___")
    print(" |       [o]       |")
    print("--|______________|--")
    
    print(f"\n\033[32m :: Device Simulator :: \033[0m\n")

def get_project_type(manifest_path):
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    language_element = root.find("language")
    if language_element is not None:
        return language_element.text.lower()
    else:
        return None
    
def launch_project(executable_path):
    try:
        subprocess.run([executable_path])
    except Exception as e:
        print(f"Execution error: {e}")

def main():
    global connection_event
    print_car()
    try:
        connection_event = threading.Event()
    	
    	#Telemetry thread creation
        telemetry_thread = threading.Thread(target=telemetry_handler)
        telemetry_thread.daemon = True
        telemetry_thread.start()
    
        connection_event.wait() #Wait that the telemtry thread sends cennected signal
        
    	#Input handler thread creation
        #input_thread = threading.Thread(target=input_handler)
        #input_thread.daemon = True
        #input_thread.start()
        
        signal.signal(signal.SIGTERM, sigterm_handler)
        telemetry_thread.join()
        #input_thread.join()

    except KeyboardInterrupt:
    	interupt_handler()
    
    
if __name__ == "__main__":
    main()
    	
