# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import ast
from typing import Any
from abc import ABC, abstractmethod

from cfg import JSON_CONFIGS_DIR_PATH
from spectre.file_handlers.json.JsonHandler import JsonHandler

class SPECTREConfigHandler(JsonHandler, ABC):
    def __init__(self, tag: str, config_type: str, **kwargs):
        self._validate_tag(tag)
        self.tag = tag
        self.config_type = config_type
        super().__init__(JSON_CONFIGS_DIR_PATH, f"{config_type}_config_{tag}", **kwargs)


    def _validate_tag(self, tag: str) -> None:
        if "_" in tag:
            raise ValueError(f"Tags cannot contain an underscore. Received {tag}.")
        if "callisto" in tag:
            raise ValueError(f'"callisto" cannot be a substring in a native tag. Received "{tag}"')


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
            dynamic_type = template.get(k)
            if dynamic_type is None:
                raise KeyError(f'Key "{k}" not found in template, expected one of {list(template.keys())}')
            try:
                if dynamic_type == bool:
                    converted_dict[k] = _convert_to_bool(v)
                elif dynamic_type == dict:
                    converted_dict[k] = _convert_to_dict(v)
                else:
                    converted_dict[k] = dynamic_type(v)
            except ValueError:
                message = f'Could not convert {k}: Received {v}, expected {dynamic_type}.'
                if dynamic_type == dict:
                    message += ' Use syntax {\\"key\\":value}.'
                raise ValueError(message)
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
            expected_type = template.get(k)
            if expected_type is None:
                raise ValueError(f'Type not found for key "{k}" in template.')
            if not isinstance(v, expected_type):
                raise TypeError(f'Expected {expected_type} for "{k}", but got {type(v)}.')

