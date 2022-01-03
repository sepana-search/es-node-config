from typing import Dict, Union
import yaml
from pathlib import Path
import os

CONFIG_FILE_PATH = "./config.yml"

class Config(dict):
    
    def __init__(self, config_file_path:str=CONFIG_FILE_PATH) -> None:
        self.path = config_file_path
        super(Config,self).__init__(**Config.load(self.path))
    
    @staticmethod
    def load(config_file_path:str) -> Dict[str, Union[str, bool]]:
        if Path(os.path.abspath(config_file_path)).is_file():
            with open(config_file_path, "r") as stream:
                config_yaml = yaml.safe_load(stream)
                return config_yaml
        else:
            print(f"Can not load {config_file_path} -> not a file")
        return {}

    def update(self, config:Dict[str, Union[str, bool]]) -> Dict[str, Union[str, bool]]:
        super().update(config)
        with open(self.path, 'w', encoding='utf8') as outfile:
            yaml.dump(dict(self), outfile, default_flow_style=False, allow_unicode=True)
