from typing import Any, Dict
import requests
import yaml
from pathlib import Path
import subprocess
import typer
import secrets


app = typer.Typer()
ES_CONFIG_FILE_PATH = "/etc/elasticsearch/elasticsearch.yml"
# ES_CONFIG_FILE_PATH = "test.yml"
CENTRAL_CONFIG_URL =  "https://dev-es-config.sepana.io"


def load_es_config(es_config_file_path:str=ES_CONFIG_FILE_PATH) -> Dict[str, Any]:
    path_copy = es_config_file_path.replace(".yml", "") + "_copy.yml"
    if Path(es_config_file_path).is_file() and not Path(path_copy).is_file():
        import shutil
        shutil.copyfile(es_config_file_path, path_copy)
    with open(es_config_file_path, "r") as stream:
        return yaml.safe_load(stream)


def save_es_config(data: Dict[str, Any], es_config_file_path:str=ES_CONFIG_FILE_PATH):
    with open(es_config_file_path, 'w', encoding='utf8') as outfile:
        yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)


def node_is_configured():
    es_config: Dict = load_es_config()
    return es_config.get("sepana-configured", False)


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
    



def update_es_config(node_config: Dict[str, Any]):
    node_config["sepana-configured"] = True
    es_config: Dict = load_es_config()
    es_config.update(node_config)
    save_es_config(es_config)


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
    if node_is_configured():
        return
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
    update_es_config(node_config)
    activate_node(host, api_key)


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

