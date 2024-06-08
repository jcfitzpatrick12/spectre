# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import ast
from typing import Any

def unpack(param: str) -> tuple:
    if '=' not in param or param.startswith('=') or param.endswith('='):
        raise ValueError(f'Invalid format: "{param}". Expected "KEY=VALUE".')
    return tuple(map(str.strip, param.split('=', 1)))

# converts the params list where each element is of the form "KEY=VALUE" 
# into a dict {"key": "value" , ...}
# no type conversion is performed, all values in the output dict are string
def params_list_to_string_valued_dict(params: list) -> dict:
    return {k: v for k, v in (unpack(param) for param in params)}

def convert_types(string_valued_dict: dict, template: dict) -> dict:
    type_converted_dict = {}
    for key, string_value in string_valued_dict.items():          
        dynamic_type = template.get(key)

        template_keys = list(template.keys())
        if dynamic_type is None:
            raise KeyError(f"The key \"{key}\" is not found in template, expected one of {template_keys}")
        
        try:
            if dynamic_type == bool:
                # need a specific implementation for boolean types
                type_converted_dict[key] = convert_to_bool(string_value)
            elif dynamic_type == dict:
                # need a specific implementation for dictionaries
                type_converted_dict[key] = convert_to_dict(string_value)
            else:
                type_converted_dict[key] = dynamic_type(string_value)

        except ValueError as e:
            value_error_message = f'Could not convert type for {key}. Received: {string_value} but expected {dynamic_type}.'
            if dynamic_type == dict:
                value_error_message = value_error_message + ' Try the syntax {\\\"key\\\":value}.'

            raise ValueError(value_error_message)
        
    return type_converted_dict


def convert_to_dict(string_value: str) -> dict:
    return ast.literal_eval(string_value)


def convert_to_bool(string_value: str) -> bool:
    if string_value.lower() in ('true', '1', 't', 'y', 'yes'):
        return True
    elif string_value.lower() in ('false', '0', 'f', 'n', 'no'):
        return False
    else:
        raise ValueError(f"Cannot convert {string_value} to bool.")


def validate_keys(input_dict: dict, template: dict, ignore_keys: list = None) -> None:
    template_keys = set(template.keys())
    keys_to_check = set(input_dict.keys())

    if ignore_keys:
        ignore_keys_type = type(ignore_keys)
        if not ignore_keys_type == list:
            raise TypeError(f"ignore_keys must be of type list. Received: {ignore_keys_type}")
        ignore_keys = set(ignore_keys)
    else:
        ignore_keys = set()

    missing_keys = template_keys - keys_to_check
    invalid_keys = keys_to_check - template_keys  - ignore_keys

    if missing_keys or invalid_keys:
        errors = []
        if missing_keys:
            errors.append(f"Missing keys: {', '.join(missing_keys)}.")

        if invalid_keys:
            errors.append(f"Invalid keys: {', '.join(invalid_keys)}.")
        raise KeyError("Key errors found! " + " ".join(errors))
    

def validate_types(input_dict: dict, template: dict, ignore_keys: list = []) -> None:
        # check the types match between the values of the capture config and the template
        for key, value in input_dict.items():
            if key in ignore_keys:
                continue
            expected_type = template.get(key)
            if expected_type is None:
                raise ValueError(f"Cannot find type in template for the key \"{key}\".")
            if not isinstance(value, expected_type):
                raise TypeError(f"Expected {expected_type}, but received {value} which is of type {type(value)}.")
            

def inject_dict(input_dict: dict, overwrite_dict: dict):
    for key, value in overwrite_dict.items():
        input_dict[key] = value
    return input_dict


def update_key_value(input_dict: dict, key: Any, value: Any) -> dict:
    valid_keys = list(input_dict.keys())
    if not key in valid_keys:
        raise KeyError(f"Key '{key}' not found. expected one of '{valid_keys}'")
    input_dict[key] = value
    return input_dict