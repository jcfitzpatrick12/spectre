# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from typing import Any
from abc import ABC
import ast

from spectre.file_handlers.base import BaseFileHandler
from spectre.cfg import (
    JSON_CONFIGS_DIR_PATH
)
from spectre.exceptions import (
    InvalidTagError
)

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
        try: 
            d[key] = value
        except KeyError:
            valid_keys = list(d.keys())
            raise KeyError(f"Key '{key}' not found. expected one of '{valid_keys}'")

        self.save(d, doublecheck_overwrite=doublecheck_overwrite)
        return
    

class SPECTREConfigHandler(JsonHandler, ABC):
    def __init__(self, tag: str, config_type: str, **kwargs):
        self._validate_tag(tag)
        self.tag = tag
        self.config_type = config_type
        super().__init__(JSON_CONFIGS_DIR_PATH, f"{config_type}_config_{tag}", **kwargs)


    def _validate_tag(self, tag: str) -> None:
        if "_" in tag:
            raise InvalidTagError(f"Tags cannot contain an underscore. Received {tag}.")
        if "callisto" in tag:
            raise InvalidTagError(f'"callisto" cannot be a substring in a native tag. Received "{tag}"')


    def _params_list_to_string_valued_dict(self, params: list) -> dict[str, str]:
        def _unpack(param: str) -> tuple:
            if not param or '=' not in param or param.startswith('=') or param.endswith('='):
                raise ValueError(f'Invalid format: "{param}". Expected "KEY=VALUE".')
            return tuple(map(str.strip, param.split('=', 1)))
        return {k: v for k, v in map(_unpack, params)}


    def _convert_types(self, d: dict[str, str], template: dict) -> dict[str, Any]:
        def _convert_to_dict(v: str) -> dict:
            return ast.literal_eval(v)
        def _convert_to_bool(v: str) -> bool:
            v = v.lower()
            if v in ('true', '1', 't', 'y', 'yes'):
                return True
            if v in ('false', '0', 'f', 'n', 'no'):
                return False
        
            raise ValueError(f'Cannot convert {v} to bool.')
        
        converted_dict = {}
        for k, v in d.items():
            try:
                dynamic_type = template[k]
            except KeyError:
                raise KeyError(f'Key "{k}" not found in template, expected one of {list(template.keys())}')
            try:
                if dynamic_type == bool:
                    converted_dict[k] = _convert_to_bool(v)
                elif dynamic_type == dict:
                    converted_dict[k] = _convert_to_dict(v)
                else:
                    converted_dict[k] = dynamic_type(v)
            except ValueError:
                error_message = f'Could not convert value at {k}: Received {v}, expected {dynamic_type.__name__}.'
                if dynamic_type == dict:
                    error_message += ' Use syntax {\\"key\\":value}.'
                raise ValueError(error_message)
        return converted_dict
    

    def type_cast_params(self, 
                         params: list[str], 
                         template: dict[str, type], 
                         validate_against_template: bool = True,
                         ignore_keys: list = []) -> dict[str, Any]:
        d = self._params_list_to_string_valued_dict(params)
        d = self._convert_types(d, template)
        if validate_against_template:
            self.validate_against_template(d, template, ignore_keys=ignore_keys)
        return d


    def validate_against_template(self, d: dict, template: dict, ignore_keys: list = []) -> None:
        self._validate_keys(d, template, ignore_keys=ignore_keys)
        self._validate_types(d, template, ignore_keys=ignore_keys)
        return
    

    def _validate_keys(self, input_dict: dict, template: dict, ignore_keys: list = []) -> None:

        template_keys = set(template.keys())
        input_keys = set(input_dict.keys())
        ignore_keys = set(ignore_keys)

        missing_keys = template_keys - input_keys
        invalid_keys = input_keys - template_keys - ignore_keys

        if missing_keys or invalid_keys:
            error_messages = []
            if missing_keys:
                error_messages.append(f"Missing keys: {', '.join(missing_keys)}.")
            if invalid_keys:
                error_messages.append(f"Invalid keys: {', '.join(invalid_keys)}.")
            raise KeyError("Key errors found! " + " ".join(error_messages))


    def _validate_types(self, d: dict, template: dict, ignore_keys: list = []) -> None:
        for k, v in d.items():
            if k in ignore_keys:
                continue
            try:
                expected_type = template[k]
            except KeyError:
                error_message = f'Type not found for key "{k}" in template.'
                raise KeyError(error_message)
            if not isinstance(v, expected_type):
                raise TypeError(f'Expected {expected_type} for "{k}", but got {type(v)}.')


class FitsConfigHandler(SPECTREConfigHandler):
    def __init__(self, tag: str, **kwargs):
        super().__init__(tag, "fits", **kwargs)

    @classmethod
    def get_template(cls) -> dict:
        return {
            "ORIGIN": str,
            "TELESCOP": str,
            "INSTRUME": str,
            "OBJECT": str,
            "OBS_LAT": float,
            "OBS_LONG": float,
            "OBS_ALT": float
        }


    def template_to_command(self, tag: str, as_string = False) -> str:
        command_as_list = ["spectre", "create", "fits-config", "-t", tag]
        template = self.get_template()
        for key, value in template.items():
            command_as_list += ["-p"]
            command_as_list += [f"{key}={value.__name__}"]
        if as_string:
            return " ".join(command_as_list)
        else:
            return command_as_list
        

    def save_params_as_fits_config(self, 
                                   params: list[str], 
                                   doublecheck_overwrite: bool = True
                                   ) -> None:
        d = self.type_cast_params(params, self.get_template())
        self.save(d, doublecheck_overwrite=doublecheck_overwrite)
        return
    
    
class CaptureConfigHandler(SPECTREConfigHandler):
    def __init__(self, tag: str, **kwargs):
        super().__init__(tag, "capture", **kwargs)