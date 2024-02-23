# GrafanaDashboards
These are the grafana dashboards for reading and analize data from AWS timestrea.

## Requirements
Instructions to make platform ready for the grafana server use, in particular for the AWS credentials:
sudo cp -r ~/.aws /usr/share/grafana/
sudo chmod 777 /usr/share/grafana/.aws/credentials

## Usage
Instructions and information on how to run the grafana server:
systemctl start grafana-server

