# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from typing import Any

from spectre.file_handlers.base import BaseFileHandler

class JsonHandler(BaseFileHandler):
    def __init__(self, parent_path: str, base_file_name: str, **kwargs):
        super().__init__(parent_path, base_file_name, extension = "json", **kwargs)
        return 
    
    
    def read(self) -> dict:
        with open(self.file_path, 'r') as f:
            return json.load(f)
        

    def save(self, d: dict, doublecheck_overwrite: bool = True) -> None:
        self.make_parent_path()

        if self.exists() and doublecheck_overwrite:
            self.doublecheck_overwrite()
        
        with open(self.file_path, 'w') as file:
            json.dump(d, file, indent=4)


    def update_key_value(self, 
                         key: str, 
                         value: Any, 
                         doublecheck_overwrite: bool = True) -> None:
        d = self.read() 
        valid_keys = list(d.keys())
        if not key in valid_keys:
            raise KeyError(f"Key '{key}' not found. expected one of '{valid_keys}'")
        d[key] = value
        self.save(d, doublecheck_overwrite=doublecheck_overwrite)
        return

