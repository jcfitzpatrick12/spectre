# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC, abstractmethod
from typing import Callable, Any

from spectre.file_handlers.json.CaptureConfigHandler import CaptureConfigHandler


class BaseReceiver(ABC):
    def __init__(self, name: str, mode: str = None):
        self.name = name
            
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
            raise KeyError(f"Mode key mismatch for the receiver {self.name}. Could not define valid modes.")


    def set_mode(self, mode: str) -> None:
        if not mode in self.valid_modes:
            raise ValueError(f"{mode} is not a defined mode for the receiver {self.name}. Expected one of {self.valid_modes}.")
        self.mode = mode


    def mode_set(self):
        return (self.mode is not None)
    
    
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


    def get_template(self) -> dict[str, Any]:
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


    def save_params_as_capture_config(self, tag: str, params: list[str], doublecheck_overwrite: bool = True) -> None:
        capture_config_handler = CaptureConfigHandler(tag)
        template = self.get_template()
        capture_config = capture_config_handler.type_cast_params(params, template) # type cast the params list according to the active template
        self.save_capture_config(capture_config, doublecheck_overwrite=doublecheck_overwrite)


    def save_capture_config(self, tag: str, capture_config: dict, doublecheck_overwrite: bool = True) -> None:
        capture_config_handler = CaptureConfigHandler(tag)
        # basic validation against the template
        capture_config_handler.validate_against_template(capture_config, 
                                                         self.get_template(), 
                                                         ignore_keys=['receiver', 'mode', 'tag'])
        # validate against receiver-specific constraints in the current mode
        self.validate(capture_config)
        # update the extra metadata
        capture_config.update({"receiver": self.name, "mode": self.mode, "tag": tag})
        # and finally, save the validated capture config to a JSON
        capture_config_handler.save(capture_config, doublecheck_overwrite = doublecheck_overwrite)
        return


    def load_capture_config(self, tag: str) -> dict:
        capture_config_handler = CaptureConfigHandler(tag)
        capture_config = capture_config_handler.read()

        if capture_config['receiver'] != self.name:
            raise ValueError(f"Capture config receiver mismatch for tag '{tag}'. Expected '{self.name}', got '{capture_config['receiver']}'.")
        
        if capture_config['mode'] != self.mode:
            raise ValueError(f"Mode mismatch for tag '{tag}'. Expected '{self.mode}', got '{capture_config['mode']}'.")

        self.validate(capture_config)
        return capture_config


    def template_to_command(self, tag: str, as_string: bool = False) -> str:
        command_as_list = ["spectre", "create", "capture-config", 
                           "--tag", tag, 
                           "--receiver", self.name, 
                           "--mode", self.mode]
        template = self.get_template()
        for key, value in template.items():
            command_as_list.extend(["-p", f"{key}={value.__name__}"])

        return " ".join(command_as_list) if as_string else command_as_list
