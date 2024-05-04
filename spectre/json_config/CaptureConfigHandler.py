import os

from spectre.json_config.JsonConfigHandler import JsonConfigHandler

class CaptureConfigHandler(JsonConfigHandler):
    def __init__(self, tag: str):
        if tag == None:
            raise ValueError(f'tag cannot be None. Received {tag}.')
        
        if "_" in tag:
            raise ValueError(f"Tags cannot contain an underscore. Received {tag}.")
        
        name = f"capture_config_{tag}"
        super().__init__(name)
    


    

    
