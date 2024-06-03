import os

from spectre.json_config.JsonConfigHandler import JsonConfigHandler

class CaptureConfigHandler(JsonConfigHandler):
    def __init__(self, tag: str):
        super().__init__("capture", tag)
    


    

    
