import os

from spectre.cfg.json_config.JsonConfig import JsonConfig

class CaptureConfig(JsonConfig):
    def __init__(self, tag: str, json_configs_dir: str):
        if tag == None:
            raise ValueError(f'tag cannot be None. Received {tag}.')
        
        if "_" in tag:
            raise ValueError(f"Tags cannot contain an underscore. Received {tag}.")
        
        name = f"capture_config_{tag}"
        super().__init__(name, json_configs_dir)
    


    

    
