# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any
import json

from spectre.file_handlers.base import BaseFileHandler

class JsonHandler(BaseFileHandler):
    def __init__(self, 
                 parent_path: str, 
                 base_file_name: str,
                 extension: str = "json",
                 **kwargs):
        super().__init__(parent_path, 
                         base_file_name, 
                         extension,
                         **kwargs)
    
    
    def read(self) -> dict[str, Any]:
        with open(self.file_path, 'r') as f:
            return json.load(f)
        

    def save(self, 
             d: dict, 
             doublecheck_overwrite: bool = True) -> None:
        self.make_parent_path()

        if self.exists and doublecheck_overwrite:
            self.doublecheck_overwrite()
        
        with open(self.file_path, 'w') as file:
            json.dump(d, file, indent=4)


    def update_key_value(self, 
                         key: str, 
                         value: Any, 
                         doublecheck_overwrite: bool = True) -> None:
        d = self.read() 
        try: 
            d[key] = value
        except KeyError:
            valid_keys = list(d.keys())
            raise KeyError(f"Key '{key}' not found. expected one of '{valid_keys}'")

        self.save(d, doublecheck_overwrite=doublecheck_overwrite)