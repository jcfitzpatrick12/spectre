import os

from spectre.utils import json_helpers

class CaptureConfig:
    def __init__(self, tag, root_path):
        if tag == None:
            raise ValueError(f'tag cannot be None. Received {tag}.')
    
        self.name = f"capture_config_{tag}"
        self.root_path = root_path
    

    def load_as_dict(self):
        json_as_dict = json_helpers.load_json_as_dict(self.name, self.root_path)
        return json_as_dict
    

    def save_dict_as_json(self, config_dict, **kwargs):
        doublecheck_overwrite = kwargs.get("doublecheck_overwrite", True)
        json_helpers.save_dict_as_json(config_dict, self.name, self.root_path, doublecheck_overwrite=doublecheck_overwrite)


    def absolute_path(self,):
        return os.path.join(self.root_path,f"{self.name}.json")
    

    
