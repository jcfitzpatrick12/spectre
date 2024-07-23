# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any
import os

from cfg import CONFIG
from spectre.utils import json_helpers, file_helpers, dict_helpers

class JsonConfigHandler:
    def __init__(self, config_type: str, tag: str):
        self.set_tag(tag)
        self.config_type = config_type
        self.file = f"{config_type}_config_{tag}.json"
        self.parent_path = CONFIG.path_to_json_configs_dir
    

    def set_tag(self, tag):
        if tag == None:
            raise ValueError(f'Tag cannot be None. Received {tag}.')
        
        if "_" in tag:
            raise ValueError(f"Tags cannot contain an underscore. Received {tag}.")

        if "callisto" in tag:
            raise ValueError(f"\"callisto\" cannot be a substring in a native tag. Received \"{tag}\"")

        self.tag = tag
        return 
    
    
    def get_path(self) -> str:
        return os.path.join(self.parent_path, self.file)
    

    def load_as_dict(self) -> dict:
        file_path = self.get_path()
        json_as_dict = json_helpers.load_json_as_dict(file_path)
        return json_as_dict
    

    def save_dict_as_json(self, d: dict, doublecheck_overwrite = True) -> None:
        file_path = self.get_path()
        json_helpers.save_dict_as_json(d, file_path, doublecheck_overwrite=doublecheck_overwrite)
    

    def update_key_value(self, key: Any, value: Any, doublecheck_overwrite = False) -> None:
        try:
            json_config_dict = self.load_as_dict()
            dict_helpers.update_key_value(json_config_dict, key, value)
            self.save_dict_as_json(json_config_dict, doublecheck_overwrite=doublecheck_overwrite)
        except (IOError, PermissionError) as e:
            raise RuntimeError(f"Failed to update {self.name} at '{CONFIG.path_to_json_configs_dir}': {e}") from e


    def delete_self(self) -> None:
        if not os.path.exists(self.get_path()):
            raise FileNotFoundError(f'Could not delete {self.name}.json: {self.get_path()} does not exist.')
        else:
            file_helpers.doublecheck_delete(self.get_path())
            os.remove(self.get_path())
            