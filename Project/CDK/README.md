# CDK

This is the CDK project. It is used to create the entire AWS infrastructure for the cloud side of the project. The project follows the following schema:

thesis-repository/
|-- Book/
|   |-- ...
`-- Project/
    |-- CDK/
        |-- certificate/
        |-- files/
        |-- functions/
        |-- lambda/
        |-- repos/
        |-- stacks/
    |-- ...

## certificates

The `certificates` directory contains certificates produced by the IoT Core stack of the cdk. They are renewed at every build of the cdk.

## files

The `files` directory contains the files used for building the ec2 istances of the cdk.

## functions

The `functions` directory contains python functions that integrates the sdk code.

## lambda

The `lambda` directory contains the package projects for the lambda functions used in the cdk project.

## repos

The `repos` directory contains the package projects codecommit repositories in the cdk.

## stacks

The `stacks` directory contains code of the actual stacks of the cdk.

## Requirements
Instructions to make platform ready for the cdk use:

### aws-cli 
NB these commands will install a .zip file so it is not raccomanded to run it on the project directory
sudo apt install curl
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update

### aws cdk toolkit 
sudo apt npm install
sudo npm install n -g
sudo n stable
sudo n prune
sudo npm install -g aws-cdk
apt-get install python3-pip
python3 -m pip install -r requirements.txt


## Usage
Instructions and information on how to deploy and destroy the cdk stack:
 ### Deploy
 STATUS=deploy cdk deploy --all
NB press yes for deploy changes; since stacks are separated comment stacks that you don't want to deploy; the use of STATUS variable is necessary for sdk integration

 ### Destroy
 STATUS=destroy cdk destroy --all