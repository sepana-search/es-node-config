from typing import Any, Dict
import requests
import yaml
from pathlib import Path
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--host', help='public ip address of the node', type=str)
parser.add_argument('--api_key', help='Sepana API key', type=str)
parser.add_argument('--name', help='name for the node', type=str)
parser.add_argument('--es_config_file_path', help='es config file path', type=str, default="/etc/elasticsearch/elasticsearch.yml")
# parser.add_argument('--es_config_file_path', help='es config file path', type=str, default="test.yml")
parser.add_argument('--central_config_url', help='central config url', type=str, default="http://localhost:8000")



def load_es_config() -> Dict[str, Any]:
    args = parser.parse_args()
    ES_CONFIG_FILE_PATH = args.es_config_file_path
    path_copy = ES_CONFIG_FILE_PATH.replace(".yml", "") + "_copy.yml"
    if Path(ES_CONFIG_FILE_PATH).is_file() and not Path(path_copy).is_file():
        import shutil
        shutil.copyfile(ES_CONFIG_FILE_PATH, path_copy)
    with open(ES_CONFIG_FILE_PATH, "r") as stream:
        return yaml.safe_load(stream)


def save_es_config(data: Dict[str, Any]):
    args = parser.parse_args()
    with open(args.es_config_file_path, 'w', encoding='utf8') as outfile:
        yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)


def node_is_configured():
    es_config: Dict = load_es_config()
    return es_config.get("sepana-configured", False)


def get_node_config(host: str) -> Dict[str, Any]:
    # example config
    # node_config = {
    #     "discovery.seed_hosts": ["137.184.29.196", "137.184.26.195"],
    #     "cluster.initial_master_nodes": ["137.184.29.196"],
    #     "cluster.name": "sepana-test",
    #     "node.name": "test-node",
    #     "node.master": False,
    #     "network.host": "137.184.29.196"
    # }
    args = parser.parse_args()
    headers = {'apikey': args.api_key}
    try:
        response = requests.get(f"{args.central_config_url}/get-config?host={host}", headers=headers)
        return response.json()
    except Exception as ex:
        raise Exception(f"can not retrieve config from {args.central_config_url}")
    



def update_es_config(node_config: Dict[str, Any]):
    node_config["sepana-configured"] = True
    es_config: Dict = load_es_config()
    es_config.update(node_config)
    save_es_config(es_config)


def start():
    stat = subprocess.call(["systemctl", "is-active", "--quiet", "elasticsearch"])
    if stat != 0:  # if not active
        subprocess.call(['sudo', 'systemctl', 'start', 'elasticsearch'])


def activate_node(host: str):
    args = parser.parse_args()
    headers = {'apikey': args.api_key}
    try:
        requests.get(f"{args.central_config_url}/activate-node?host={host}", headers=headers)
    except:
        pass


def init():
    args = parser.parse_args()
    host = args.host
    if node_is_configured():
        return
    node_config = register()
    update_es_config(node_config)
    activate_node(host)


def register():
    args = parser.parse_args()
    node_config = {"host": args.host}
    if args.name:
        node_config["name"] = args.name
    try:
        headers = {'apikey': args.api_key}
        response = requests.post(f"{args.central_config_url}/register-node", json=node_config, headers=headers)
        return response.json()
    except Exception as ex:
        print(ex)
        print("Error registering the node")
        return {}
    
def clusters():
    print("register new node")
    
def stop():
    stat = subprocess.call(["systemctl", "is-active", "--quiet", "elasticsearch"])
    if stat == 0:  # if active
        subprocess.call(['sudo', 'systemctl', 'stop', 'elasticsearch'])
    print("sepana node stopped")

# if __name__ == "__main__":
#     host = None
#     if sys.argv:
#         host = sys.argv[0]
#     setup_node()
