import os

from spectre.cfg.json_config.JsonConfig import JsonConfig

class CaptureConfig(JsonConfig):
    def __init__(self, tag: str, dir_path: str):
        if tag == None:
            raise ValueError(f'tag cannot be None. Received {tag}.')
    
        name = f"capture_config_{tag}"
        super().__init__(name, dir_path)
    


    

    
