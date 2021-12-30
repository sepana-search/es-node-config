from typing import Any, Dict
import requests
import subprocess
import typer
import secrets
from config import Config


app = typer.Typer()
config = Config()
ES_CONFIG_FILE_PATH = config.get("es_central_config_path")
ES_CONFIG_FILE_PATH = "test.yml"
CENTRAL_CONFIG_URL =  config.get("central_config_url")
NODE_IS_CONFIGURED = config.get("sepana_configured")
es_config = Config(ES_CONFIG_FILE_PATH)


def get_node_config(host: str, api_key:str, config_url:str=CENTRAL_CONFIG_URL) -> Dict[str, Any]:
    # example config
    # node_config = {
    #     "discovery.seed_hosts": ["137.184.29.196", "137.184.26.195"],
    #     "cluster.initial_master_nodes": ["137.184.29.196"],
    #     "cluster.name": "sepana-test",
    #     "node.name": "test-node",
    #     "node.master": False,
    #     "network.host": "137.184.29.196"
    # }
    headers = {'apikey': api_key}
    try:
        response = requests.get(f"{config_url}/get-config?host={host}", headers=headers)
        return response.json()
    except Exception as ex:
        raise Exception(f"can not retrieve config from {config_url}")


@app.command(help="start sepana node")
def start():
    stat = subprocess.call(["systemctl", "is-active", "--quiet", "elasticsearch"])
    if stat != 0:  # if not active
        subprocess.call(['sudo', 'systemctl', 'start', 'elasticsearch'])


def activate_node(host: str, api_key:str, config_url:str=CENTRAL_CONFIG_URL):
    headers = {'apikey': api_key}
    try:
        requests.get(f"{config_url}/activate-node?host={host}", headers=headers)
    except:
        pass


@app.command(help="Initialize sepana node, this will setup elasticsearch configuration")
def init(host:str = typer.Option(default=None, help="Public ip address of the node"), api_key:str = typer.Option(default=None, help="API key")):
    if NODE_IS_CONFIGURED:
        return
    fresh_init(host, api_key)


def register(host:str = None, name:str = None, api_key:str = None, config_url:str=CENTRAL_CONFIG_URL):
    node_config = {"host": host}
    if name:
        node_config["name"] = name
    try:
        headers = {'apikey': api_key}
        response = requests.post(f"{config_url}/register-node", json=node_config, headers=headers)
        return response.json()
    except Exception as ex:
        print(ex)
        print("Error registering the node")
        return {}
    
@app.command(help="get a list of a sepana node")
def clusters():
    print("get all clusters")


@app.command(help="stop sepana node")
def stop():
    stat = subprocess.call(["systemctl", "is-active", "--quiet", "elasticsearch"])
    if stat == 0:  # if active
        subprocess.call(['sudo', 'systemctl', 'stop', 'elasticsearch'])
    print("sepana node stopped")
    
@app.command(help="Initialize sepana node even when it has been done before, this will setup elasticsearch configuration with new config")
def fresh_init(host:str = typer.Option(default=None, help="Public ip address of the node"), api_key:str = typer.Option(default=None, help="API key")):
    if not host:
        host =  typer.prompt("Public ip address of the node?")
    if not api_key:
        api_key =  typer.prompt("PI key ?")
    name =  typer.prompt("Node name?", default=f"node-{secrets.token_hex(6)}")
    node_config = register(host, name, api_key)
    if not node_config.get("cluster.name"):
        print(node_config)
        print("Configuration could not be completed")
        return
    es_config.update(node_config)
    config.update({"sepana_configured" : True})
    activate_node(host, api_key)

@app.command(help="Update node config")
def update_config(es_central_config_path:str = typer.Option(default=ES_CONFIG_FILE_PATH, help="Change path to es configuration file"), 
                  central_config_url:str = typer.Option(default=CENTRAL_CONFIG_URL, help="Change central config url")):
    config.update({"es_central_config_path": es_central_config_path, "central_config_url": central_config_url})
