#!/bin/bash

echo "Starting installation"

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
sudo apt-get -y install python3-pip >/dev/null
pip install git+https://github.com/sepana-search/es-node-config

FILE=docker-compose.yml
if [ -f "$FILE" ]; then
    echo "$FILE exists."
else 
    curl -LJO https://raw.github.com/sepana-search/es-node-config/main/docker-compose.yml
fi
