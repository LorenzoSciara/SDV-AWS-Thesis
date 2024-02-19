# Project
This is the project for the job, as well as the practical example. The project follows the following schema:

thesis-repository/
|-- Book/
|   |-- ...
`-- Project/
    |-- CDK/
    |-- GrafanaDashboards/
    |-- Lorenzo_Device/
    |-- Lorenzo_Device1/
    |-- Lorenzo_Device2/
    |-- pytests/
    |-- src/
    |-- target/
    |-- TCUc/
    |-- TCUcpp/
    `-- documentation/

## CDK

The `CDK` directory contains the code for the cdk stack that is used to buld the entire AWS infrastructure. A better explaination is given in the CDK directory.

## GrafanaDashboards

The `GrafanaDashboards` directory contains the grafana json for the dashboard used for analize the data in the Timestream Database.

## Lorenzo_Device

The `Lorenzo_Device` directory contains the simulator of a hawkbit device. A better explaination is given in the Lorenzo_Device directory

## Lorenzo_Device1

The `Lorenzo_Device1` directory contains the simulator of the TCU system that create data for every component. It is the version before the update download.

## Lorenzo_Device2

The `Lorenzo_Device2` directory contains the simulator of the TCU system that create data for every component. It is the version that will be upload in the codecommit and on the hawkbit server for the update on the device.

## pytests

The `pytests` directory contains te tests for the Lorenzo_Device1 unit. they are in python and pytest tool is needed.

## src

The `src` directory contains the Java code for the Hawbit device simulator. With the use of Maven it produce the executable file responsable for the connection with the server.

## target

The `target` directory contains the results of the Maven operations on src directory.

## TCUc

The `TCUc` directory contains C code fot the simulation of a C TCU. It is used for the build phase of the codepipeline of compiled projects.

## TCUcpp

The `TCUcpp` directory contains C++ code fot the simulation of a C++ TCU. It is not used but was a possible solution for the build phase of the codepipeline of compiled projects.