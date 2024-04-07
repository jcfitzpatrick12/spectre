from spectre.utils import json_helpers
import os

class JsonConfig:
    def __init__(self, name: str, dir_path: str):
        self.name = name
        self.dir_path = dir_path

    def load_as_dict(self) -> dict:
        json_as_dict = json_helpers.load_json_as_dict(self.name, self.dir_path)
        return json_as_dict
    
    def save_dict_as_json(self, input_dict: dict, **kwargs) -> None:
        doublecheck_overwrite = kwargs.get("doublecheck_overwrite", True)
        json_helpers.save_dict_as_json(input_dict, self.name, self.dir_path, doublecheck_overwrite=doublecheck_overwrite)

    def absolute_path(self) -> str:
        return os.path.join(self.dir_path, f"{self.name}.json")
    
    def add_key_value(self, key: str, value: any) -> None:
        try:
            json_config_dict = self.load_as_dict()
            json_config_dict[key] = value
            self.save_dict_as_json(json_config_dict)
        except FileNotFoundError:
            json_config_dict = {key: value}
            self.save_dict_as_json(json_config_dict)
        except (IOError, PermissionError) as e:
            raise RuntimeError(f"Failed to update {self.name} at '{self.dir_path}': {e}") from e

    def remove_key(self, key: str) -> None:
        try:
            json_config_dict = self.load_as_dict()
            if key in json_config_dict:
                del json_config_dict[key]
                self.save_dict_as_json(json_config_dict)
            else:
                raise KeyError(f"Key '{key}' not found in '{self.name}'.")
        except FileNotFoundError:
            raise FileNotFoundError(f"The configuration file for '{self.name}' does not exist.")
        except (IOError, PermissionError) as e:
            raise RuntimeError(f"Failed to update {self.name} at '{self.dir_path}': {e}") from e
