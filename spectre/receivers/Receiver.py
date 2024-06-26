# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.utils import dict_helpers
from spectre.json_config.CaptureConfigHandler import CaptureConfigHandler

from spectre.receivers.get_mount import get_capture_config_mount, get_capture_mount

class Receiver:
    def __init__(self, 
                 receiver_name: str,
                 mode: str = None):
        self.receiver_name = receiver_name 
        self.set_mounts(receiver_name)

        if self.capture_config.valid_modes != self.capture.valid_modes:
            raise KeyError(f"Mismatch for defined valid modes between CaptureConfigHandler and Capture mounts. Check the keys.")

        # after verifying that both mounts have the same modes specified, we can safely define valid modes
        self.valid_modes = self.capture_config.valid_modes

        if mode:
            self.set_mode(mode)


    def set_mounts(self, receiver_name: str) -> None:
        self.set_capture_config_mount(receiver_name)
        self.set_capture_mount(receiver_name)


    def set_capture_config_mount(self, receiver_name: str):
        Mount = get_capture_config_mount(receiver_name)
        try:
            self.capture_config = Mount() # try and instantiate the mount
        except TypeError as e:
            raise TypeError(f"Failed to create instance of capture config mount for receiver {receiver_name}. Received the error: {e}")
        

    def set_capture_mount(self, receiver_name: str):
        Mount = get_capture_mount(receiver_name)
        try:
            self.capture = Mount()
        except TypeError as e:
            raise TypeError(f"Failed to create instance of capture mount for receiver {receiver_name}. Received the error: {e}")


    def set_mode(self, mode: str) -> None:
        if mode not in self.valid_modes:
            raise ValueError(f'{mode} is not a defined mode for the receiver: {self.receiver_name}. Need one of {self.valid_modes}')
        self.mode = mode
        return
    
    
    def get_template(self):
        return self.capture_config.get_template(self.mode)


    def start_capture(self, tags: list) -> None:
        # first check if the current mode is valid.
        if self.mode not in self.valid_modes:
            raise ValueError(f'Current receiver mode is not valid. Received {self.mode}, need one of {self.valid_modes}.')

        capture_configs = []
        for tag in tags:
            capture_config = self.get_capture_config_for_capture(tag)
            capture_configs.append(capture_config)

        # start the capture session
        self.capture.start(self.mode, capture_configs)
        return
    

    # save params to file as a capture config with tag [tag], validated according to the receiver in mode [mode]
    def save_params_as_capture_config(self, 
                                      params: list, 
                                      tag: str,
                                      doublecheck_overwrite: bool = True) -> None:
        
        # convert the user defined params to a raw_dict [key=string_value]
        string_valued_dict = dict_helpers.params_list_to_string_valued_dict(params)
        # extract the capture config template for the current mode of the receiver
        template = self.get_template()
        # verify the keys of the string valued dict against the template
        dict_helpers.validate_keys(string_valued_dict, template)
        # convert the raw dict string values to those defined in the template
        capture_config = dict_helpers.convert_types(string_valued_dict, template)
        # and finally, save the capture_config as dict. Internally performs validations on the config as specified
        # the capture config mount 
        self.save_capture_config(capture_config, 
                                 tag, 
                                 doublecheck_overwrite=doublecheck_overwrite)
        return  
    
    # method assumes the input capture config is correctly type cast in line with the template
    def save_capture_config(self, 
                            capture_config: dict, 
                            tag: str, 
                            doublecheck_overwrite: bool = True) -> None:
        # extract the capture config template for the current mode of the receiver
        template = self.get_template()
        # extract the capture config template for the current mode of the receiver
        dict_helpers.validate_keys(capture_config, template, ignore_keys=['receiver', 'mode', 'tag'])
        # validate the types according to the template
        dict_helpers.validate_types(capture_config, template, ignore_keys=['receiver', 'mode', 'tag'])
        # validate according to receiver-specific constraints
        self.capture_config.validate(capture_config, self.mode)
        
        # add two extra key values to specify the mode and the receiver name for the capture config
        capture_config['receiver'] = self.receiver_name
        capture_config['mode'] = self.mode
        capture_config['tag'] = tag
        # instantiate capture_config and save the newly constructed config_dict
        capture_config_handler = CaptureConfigHandler(tag)
        # save to file under the requested tag
        capture_config_handler.save_dict_as_json(capture_config, 
                                                 doublecheck_overwrite=doublecheck_overwrite)
        return
    

    def get_capture_config_for_capture(self, tag: str) -> dict:
        # load the requested capture config
        capture_config_handler = CaptureConfigHandler(tag)
        capture_config = capture_config_handler.load_as_dict()

        # check the mode of the capture config matches the current mode of the receiver.
        capture_config_mode = capture_config['mode']
        if self.mode != capture_config_mode:
            raise ValueError(f'Error fetching capture config for tag {tag}. Receiver must be in the same mode as that specified in capture-config. Receiver mode: {self.mode}, capture-config mode: {capture_config_mode}')
        
        # check the requested capture config matches the current receiver.
        receiver_in_capture_config = capture_config['receiver'] 
        if receiver_in_capture_config != self.receiver_name:
            raise ValueError(f'Error fetching capture config for tag {tag}. Capture config receiver must match the current receiver. Got {receiver_in_capture_config} and {self.receiver_name} respectively.')

        # validate the capture config before returning
        self.capture_config.validate(capture_config, self.mode)
        return capture_config
    
    
    def template_to_command(self, tag: str, as_string = False) -> str:
        command_as_list = ["spectre", "create", "capture-config", "-r", self.receiver_name, "-m", self.mode, "-t", tag]
        template = self.capture_config.get_template(self.mode)
        for key, value in template.items():
            command_as_list += ["-p"]
            command_as_list += [f"{key}={value.__name__}"]
        if as_string:
            return " ".join(command_as_list)
        else:
            return command_as_list
        


 




