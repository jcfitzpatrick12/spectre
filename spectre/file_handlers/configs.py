# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any, Optional, Type, Tuple
from abc import ABC
import ast

from spectre.file_handlers.json import JsonHandler
from spectre.cfg import JSON_CONFIGS_DIR_PATH
from spectre.exceptions import (
    InvalidTagError
)


def _unpack_param(param: str) -> list[str, str]:
    """Seperate a string of the form "a=b" into a list [a,b]."""
    if not param or '=' not in param:
        raise ValueError(f'Invalid format: "{param}". Expected "KEY=VALUE".')
    if param.startswith('=') or param.endswith('='):
        raise ValueError(f'Invalid format: "{param}". Expected "KEY=VALUE".')
    # remove leading and trailing whitespace.
    param = param.strip()
    return param.split('=', 1)


def _params_to_string_dict(params: list[str]) -> dict[str, str]:
    """Converts a list with string elements of the form "a=b" into a dictionary where the key value pairs are "a": "b"."""
    d = {}
    for param in params:
        key, value = _unpack_param(param)
        d[key] = value
    return d


def _convert_to_dict(v: str) -> dict:
    """Evaluate literally a string containing a Python dictionary expression."""
    return ast.literal_eval(v)


def _convert_to_bool(v: str) -> bool:
    """Evaluate literally a string representation of a boolean as a boolean"""
    v = v.lower()
    if v in ('true', '1', 't', 'y', 'yes'):
        return True
    if v in ('false', '0', 'f', 'n', 'no'):
        return False
    raise ValueError(f'Cannot convert {v} to bool.')
    

def _convert_string_to_type(value: str, 
                           target_type: Type) -> Any:
    """Cast a string as the target type."""
    if target_type == bool:
        return _convert_to_bool(value)
    elif target_type == dict:
        return _convert_to_dict(value)
    return target_type(value)


def _type_cast_string_dict(d: dict[str, str], 
                           type_template: dict[str, Type]) -> dict[str, Any]:
    """Cast the values of the input dictionary according to a type template."""
    casted_d = {}
    for key, value in d.items():
        target_type = type_template.get(key)
        if target_type is None:
            raise KeyError(f'Key "{key}" not found in type template. Expected keys: {list(type_template.keys())}')
        try:
            casted_d[key] = _convert_string_to_type(value, target_type)
        except ValueError:
            raise ValueError(f'Failed to convert key "{key}" with value "{value}" to {target_type.__name__}.')
    return casted_d


def _validate_keys(d: dict[str, Any], 
                   type_template: dict[str, type], 
                   ignore_keys: Optional[list] = None) -> None:
    """Validate that the keys in the input dictionary map one-to-one to the input type template."""
    if ignore_keys is None:
        ignore_keys = []

    type_template_keys = set(type_template.keys())
    input_keys = set(d.keys())
    ignore_keys = set(ignore_keys)

    missing_keys = type_template_keys - input_keys
    invalid_keys = input_keys - type_template_keys - ignore_keys

    errors = []
    
    if missing_keys:
        errors.append(f"Missing keys: {', '.join(missing_keys)}")

    if invalid_keys:
        errors.append(f"Invalid keys: {', '.join(invalid_keys)}")
    
    if errors:
        raise KeyError("Key errors found! " + " ".join(errors))


def _validate_types(d: dict[str, Any], 
                    type_template: dict[str, type], 
                    ignore_keys: Optional[list] = None) -> None:
    """Validate the types in the input dictionary are consistent with the input type template."""

    if ignore_keys is None:
        ignore_keys = []
        
    for k, v in d.items():
        if k in ignore_keys:
            continue
        expected_type = type_template[k]
        if expected_type is None:
            raise KeyError(f'Type not found for key "{k}" in the type template.')
        
        if not isinstance(v, expected_type):
            raise TypeError(f'Expected {expected_type} for "{k}", but got {type(v)}.')


def validate_against_type_template(d: dict[str, Any], 
                                   type_template: dict[str, type], 
                                   ignore_keys: Optional[list] = None) -> None:
    """Validates the keys and values of the input dictionary, according to the input type template."""
    _validate_keys(d, 
                   type_template, 
                   ignore_keys = ignore_keys)
    _validate_types(d, 
                    type_template, 
                    ignore_keys = ignore_keys)


def type_cast_params(params: list[str], 
                     type_template: dict[str, type]) -> dict[str, Any]:
    d = _params_to_string_dict(params)
    return _type_cast_string_dict(d, 
                                  type_template)



class SPECTREConfig(JsonHandler, ABC):
    def __init__(self, 
                 tag: str, 
                 config_type: str, 
                 **kwargs):
        self._validate_tag(tag)
        self._tag = tag
        self._config_type = config_type

        self._dict = None # cache
        super().__init__(JSON_CONFIGS_DIR_PATH, 
                         f"{config_type}_config_{tag}", 
                         **kwargs)


    @property
    def tag(self) -> str:
        return self._tag
    

    @property
    def config_type(self) -> str:
        return self._config_type
    

    @property
    def dict(self) -> dict[str, Any]:
        if self._dict is None:
            self._dict = self.read()
        return self._dict
    

    def _validate_tag(self, tag: str) -> None:
        if "_" in tag:
            raise InvalidTagError(f"Tags cannot contain an underscore. Received {tag}")
        if "callisto" in tag:
            raise InvalidTagError(f'"callisto" cannot be a substring in a native tag. Received "{tag}"')

    
    def __getitem__(self, subscript: str | int) -> Any:
        return self.dict[subscript]
    

    def get(self, key: str) -> Any:
        return self.dict.get(key)
    
    
    def update(self, d: dict) -> None:
        self._dict.update(d)

    
    def items(self):
        return self._dict.items()
    
    
    def keys(self):
        return self._dict.keys()
    
    
    def values(self):
        return self._dict.values()

class FitsConfig(SPECTREConfig):

    type_template = {
        "ORIGIN": str,
        "TELESCOP": str,
        "INSTRUME": str,
        "OBJECT": str,
        "OBS_LAT": float,
        "OBS_LONG": float,
        "OBS_ALT": float
    }

    def __init__(self, 
                 tag: str, 
                 **kwargs):
        super().__init__(tag, 
                         "fits", 
                         **kwargs)

    def get_create_fits_config_cmd(self, 
                                   tag: str, 
                                   as_string: bool = False) -> list[str] | str:
        command_as_list = ["spectre", "create", "fits-config", "-t", tag]
        for key, value in self.type_template.items():
            command_as_list += ["-p"]
            command_as_list += [f"{key}={value.__name__}"]
        if as_string:
            return " ".join(command_as_list)
        else:
            return command_as_list
        

    def save_params(self, 
                    params: list[str], 
                    doublecheck_overwrite: bool = True
                    ) -> None:
        d = type_cast_params(params, 
                             self.type_template)
        self.save(d, 
                  doublecheck_overwrite = doublecheck_overwrite)

    
    def read(self) -> None:
        try:
            return super().read()
        except FileNotFoundError as e:
            raise FileNotFoundError((
                f"A fits config could not be found with tag {self.tag}. " 
                f"Received the following error: {e}"
            ))
        

    
class CaptureConfig(SPECTREConfig):
    def __init__(self, 
                 tag: str, 
                 **kwargs):
        super().__init__(tag, 
                         "capture", 
                         **kwargs)

    def read(self) -> None:
        try:
            return super().read()
        except FileNotFoundError as e:
            raise FileNotFoundError((
                f"A capture config could not be found with tag {self.tag}. " 
                f"Received the following error: {e}"
            ))
        

    def get_receiver_metadata(self) -> Tuple[str, str]:

        receiver_name, mode = self.get("receiver"), self.get("mode")

        if receiver_name is None:
            raise ValueError("Invalid capture config! Receiver name is not specified.")
    
        if mode is None:
            raise ValueError("Invalid capture config! Receiver mode is not specified.")
        
        return receiver_name, mode