# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC, abstractmethod
from typing import Callable

from spectre.utils import dict_helpers
from spectre.json_config.CaptureConfigHandler import CaptureConfigHandler


class BaseReceiver(ABC):
    def __init__(self, receiver_name: str, mode: str = None):
        self.receiver_name = receiver_name
            
        self._set_capture_methods()
        self._set_templates()
        self._set_validators()
        self._set_valid_modes()

        if not mode is None:
            self.set_mode(mode)


    @abstractmethod
    def _set_capture_methods(self) -> None:
        pass


    @abstractmethod
    def _set_validators(self) -> None:
        pass


    @abstractmethod
    def _set_templates(self) -> None:
        pass

    
    # ensure that all receiver maps define the same modes for the receiver
    def _set_valid_modes(self) -> None:
        capture_method_modes = list(self.capture_methods.keys())
        validator_modes = list(self.validators.keys())
        template_modes = list(self.templates.keys())

        if capture_method_modes == validator_modes == template_modes:
            self.valid_modes = capture_method_modes
        else:
            raise KeyError(f"Mode key mismatch for the receiver {self.receiver_name}. Could not define valid modes.")


    def set_mode(self, mode: str) -> None:
        if not mode in self.valid_modes:
            raise ValueError(f"{mode} is not a defined mode for the receiver {self.receiver_name}. Expected one of {self.valid_modes}.")
        self.mode = mode



    def get_capture_method(self) -> Callable:
        capture_method = self.capture_methods.get(self.mode)
        if capture_method is None:
            raise ValueError(f"Invalid mode '{self.mode}'. Valid modes are: {self.valid_modes}")
        return capture_method


    def get_validator(self) -> Callable:
        validator = self.validators.get(self.mode)
        if validator is None:
            raise ValueError(f"Invalid mode '{self.mode}'. Valid modes are: {self.valid_modes}")
        return validator


    def get_template(self) -> dict:
        template = self.templates.get(self.mode)
        if template is None:
            raise ValueError(f"Invalid mode '{self.mode}'. Valid modes are: {self.valid_modes}")
        return template


    def validate(self, capture_config: dict) -> None:
        validator = self.get_validator()
        validator(capture_config)
        return


    def start_capture(self, tags: list) -> None:
        capture_configs = [self.load_capture_config(tag) for tag in tags]
        capture_method = self.get_capture_method()
        capture_method(capture_configs)
        return


    def save_params_as_capture_config(self, params: list, tag: str, doublecheck_overwrite: bool = True) -> None:
        string_valued_dict = dict_helpers.params_list_to_string_valued_dict(params)
        template = self.get_template()
        capture_config = dict_helpers.convert_types(string_valued_dict, template)
        self.save_capture_config(tag, capture_config, doublecheck_overwrite)
        return


    def save_capture_config(self, tag: str, capture_config: dict, doublecheck_overwrite: bool = True) -> None:
        template = self.get_template()
        dict_helpers.validate_keys(capture_config, template, ignore_keys=['receiver', 'mode', 'tag'])
        dict_helpers.validate_types(capture_config, template, ignore_keys=['receiver', 'mode', 'tag'])
        self.validate(capture_config)
        capture_config.update({'receiver': self.receiver_name, 'mode': self.mode, 'tag': tag})

        capture_config_handler = CaptureConfigHandler(tag)
        capture_config_handler.save_dict_as_json(capture_config, doublecheck_overwrite=doublecheck_overwrite)
        return


    def load_capture_config(self, tag: str) -> dict:
        capture_config_handler = CaptureConfigHandler(tag)
        capture_config = capture_config_handler.read()

        if capture_config['receiver'] != self.receiver_name:
            raise ValueError(f"Capture config receiver mismatch for tag '{tag}'. Expected '{self.receiver_name}', got '{capture_config['receiver']}'.")

        if capture_config['mode'] != self.mode:
            raise ValueError(f"Mode mismatch for tag '{tag}'. Expected '{self.mode}', got '{capture_config['mode']}'.")

        self.validate(capture_config)
        return capture_config


    def template_to_command(self, tag: str, as_string: bool = False) -> str:
        command_as_list = ["spectre", "create", "capture-config", "-r", self.receiver_name, "-m", self.mode, "-t", tag]
        template = self.get_template()
        for key, value in template.items():
            command_as_list.extend(["-p", f"{key}={value.__name__}"])

        return " ".join(command_as_list) if as_string else command_as_list
