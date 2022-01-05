from typing import Any, Dict
import requests
import subprocess
import typer
import secrets
from sepana.config import Config


app = typer.Typer()
config = Config()
ES_CONFIG_FILE_PATH = config.get("es_central_config_path")
CENTRAL_CONFIG_URL =  config.get("central_config_url")
NODE_IS_CONFIGURED = config.get("sepana_configured")
es_config = Config(ES_CONFIG_FILE_PATH)


def mount_docker_es_conf_file():
    if not ES_CONFIG_FILE_PATH:
        return
    docker_compose = Config("docker-compose.yml")
    for value in docker_compose.get("services", {}).values():
        if "docker.elastic.co/elasticsearch" in value.get("image"):
            volumes = value.get("volumes", [])
            volumes.append(f"{ES_CONFIG_FILE_PATH}:{config.get('docker_es_config_path')}")
            value["volume"] = volumes
    docker_compose.update({"services": docker_compose.get("services")})
    print(docker_compose)


def get_node_config(host: str, api_key:str, conf_type:str = "default", config_url:str=CENTRAL_CONFIG_URL) -> Dict[str, Any]:
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
        response = requests.get(f"{config_url}/get-config?host={host}&conf_type={conf_type}", headers=headers)
        return response.json()
    except Exception as ex:
        raise Exception(f"can not retrieve config from {config_url}")


@app.command(help="start sepana node")
def start():
    if config.get("conf_type", "").lower() == "docker":
        subprocess.call(["docker-compose", "up"])
    else:
        stat = subprocess.call(["systemctl", "is-active", "--quiet", "elasticsearch"])
        if stat != 0:  # if not active
            subprocess.call(['sudo', 'systemctl', 'start', 'elasticsearch'])


def activate_node(host: str, api_key:str, config_url:str=CENTRAL_CONFIG_URL):
    headers = {'apikey': api_key}
    try:
        requests.get(f"{config_url}/activate-node?host={host}", headers=headers)
    except:
        pass


@app.command(help="Initialize sepana node, this will setup elasticsearch configurations")
def init(host:str = typer.Option(default=None, help="Public ip address of the node"), conf_type:str = typer.Option(default="default", help="Configuration type docker or default"), api_key:str = typer.Option(default=None, help="API key")):
    if NODE_IS_CONFIGURED:
        return
    fresh_init(host, api_key, conf_type)


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
    if config.get("conf_type", "").lower() == "docker":
        subprocess.call(["docker-compose", "down"])
    else:
        stat = subprocess.call(["systemctl", "is-active", "--quiet", "elasticsearch"])
        if stat == 0:  # if active
            subprocess.call(['sudo', 'systemctl', 'stop', 'elasticsearch'])
    
@app.command(help="Initialize sepana node even when it has been done before, this will setup elasticsearch configuration with new config")
def fresh_init(host:str = typer.Option(default=None, help="Public ip address of the node"), api_key:str = typer.Option(default=None, help="API key"), conf_type:str = typer.Option(default=None, help="Configuration type docker or default")):
    if not host:
        host =  typer.prompt("Public ip address of the node?")
    if not api_key:
        api_key =  typer.prompt("PI key ?")
    name =  typer.prompt("Node name?", default=f"node-{secrets.token_hex(6)}")
    if not conf_type:
        conf_type = typer.prompt("Configuration type default or docker", default="default")
    es_config_path =  typer.prompt("Elasticsearh config file path?", default=f"{ES_CONFIG_FILE_PATH}")
    if ES_CONFIG_FILE_PATH != es_config_path:
        config.update({"es_central_config_path": es_config_path})
        es_config = Config(es_config_path)
    register(host, name, api_key)
    node_config = get_node_config(host, api_key, conf_type)
    if not node_config.get("cluster.name"):
        print(node_config)
        print("Configuration could not be completed")
        return
    es_config.update(node_config)
    config.update({"sepana_configured" : True, "conf_type":conf_type})
    activate_node(host, api_key)
    if conf_type == "docker":
        mount_docker_es_conf_file()

@app.command(help="Update node config")
def update_config(es_config_path:str = typer.Option(default=ES_CONFIG_FILE_PATH, help="Change path to es configuration file"), 
                  central_config_url:str = typer.Option(default=CENTRAL_CONFIG_URL, help="Change central config url")):
    config.update({"es_central_config_path": es_config_path, "central_config_url": central_config_url})
