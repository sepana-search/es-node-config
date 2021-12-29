# ES Node Config

## Name
ES Node Config

## Description
This is used to configure elasticsearch node.

## Installation
pip install git+https://github.com/sepana-search/es-node-config

## Usage
After installation. There are couple of comand line script available for you like; 
- sepanactl --help => for available commands
- sepanactl init => this is uded to initialize the node. It will configure the node
- sepanaclt start => this will start already configure sepana node. It needs no arguments
- sepanaclt stop => this will stop the runnin node. It needs no arguments

sepanaclt init 
- prompt for host public ip => 137.184.26.195
- prompt for api_key => 5e8b2cbf-f762-4a75-97e2-58fa9df8a84a 

Or just do

  sepanactl init --host=137.184.29.196 --api-key=5e8b2cbf-f762-4a75-97e2-58fa9df8a84a

