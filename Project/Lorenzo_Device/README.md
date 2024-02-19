# Lorenzo_Device

This is the Hawkbit device project. It is used to simulate a device vehicle that downloads update from Hawkbit server. The Device Simulator could run on ubuntu 22.0 or on arm ruspberry. The project follows the following schema:

```bash
thesis-repository/
|-- Book/
    |-- ...
|-- Project/
    |-- Lorenzo_Device/
        |-- Permanent/
            |-- Certificates/
            |-- HawkbitClient/
            |-- Watchdog/
        |-- TCU/
        |-- OS.py
        |-- start.sh
    |-- ...
```

## Permanent

The `Permanent` directory contains all code for manage the connection and download of files from Hawkbit server.

## TCU

The `TCU` directory contains all code for simulate TCU datas.

## OS.py

The `OS.py` file manage the data that are produced to the TCU and send it to the AWS IoT Core service (and to Timestream database).

## OS.py

The `OS.py` file manage all the files of the device simulator.

## Requirements
Instructions to make platform ready for the device simulator use:

sudo apt install openjdk-17-jdk -y
sudo apt-get install python3-pip
python3 -m pip install -r requirements.txt

## Usage
Instructions and information on how to run the device simulator:

./start.sh
