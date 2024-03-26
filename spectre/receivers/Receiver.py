from spectre.utils import json_helpers, param_to_cc_dict_helpers
from spectre.capture_config.CaptureConfig import CaptureConfig

# it is important to import the receivers library
# since the decorators only take effect on import
# importing will mean the mount maps will be populated as intended
import spectre.receivers.library

from spectre.receivers.mount_register import get_capture_config_mount, get_capture_mount

class Receiver:
    def __init__(self, receiver_name):
        self.receiver_name = receiver_name
        self.mode = None # must be set manually for class instances.
        # capture config mount are receiver specific
        self.capture_config = get_capture_config_mount(receiver_name)
        # capture mount is receiver specific
        self.capture = get_capture_mount(receiver_name)

        if self.capture_config.valid_modes != self.capture.valid_modes:
            raise KeyError(f"Mismatch for defined valid modes between CaptureConfig and Capture mounts. Check the keys.")


    def set_mode(self, mode):
        if mode not in self.capture_config.valid_modes:
            raise ValueError(f'{mode} is not a defined mode for the receiver: {self.receiver_name}. Need one of {self.capture_config.valid_modes}')
        self.mode = mode


    # save params to file as a capture config with tag [tag], validated according to the receiver in mode [mode]
    def save_capture_config(self, params, tag, root_path):
        # extract the capture config template for the current mode of the receiver
        template = self.capture_config.get_template(self.mode)

        # convert the user defined params to a raw_dict [key=string_value]
        raw_dict = param_to_cc_dict_helpers.params_to_raw_dict(params)

        # fetch the template for the current mode
        template = self.capture_config.get_template(self.mode)

        # verify the keys of the raw dict against the template
        param_to_cc_dict_helpers.validate_keys(raw_dict, template)
        
        # convert the raw dict string values to those defined in the template
        capture_config_as_dict = param_to_cc_dict_helpers.convert_types(raw_dict, template)  

        # extract the validator function for the current mode.
        # validator = self.capture_config.get_validator(self.mode)

        # validate according to receiver-specific constraints
        self.capture_config.validate(capture_config_as_dict, self.mode)

        # add two extra key values to specify the mode and the receiver name for the capture config
        capture_config_as_dict['receiver'] = self.receiver_name
        capture_config_as_dict['mode'] = self.mode
        
        # instantiate capture_config and save the newly constructed config_dict
        capture_config_instance = CaptureConfig(tag, root_path)
        # save to file under the requested tag
        capture_config_instance.save_dict_as_json(capture_config_as_dict)
        pass   

    
    def do_capture(self, tag, path_to_capture_configs):
        # first check if the current mode is valid.
        if self.mode not in self.capture_config.valid_modes:
            raise ValueError(f'Current receiver mode is not valid. Received {self.mode}, need one of {self.capture_config.valid_modes}.')
        
        # then load the requested capture config
        capture_config = CaptureConfig(tag, path_to_capture_configs)
        capture_config_dict = capture_config.load_as_dict()


        # check the mode of the capture config matches the current mode of the receiver.
        if self.mode != capture_config_dict['mode']:
            raise ValueError(f'Receiver must be in the same mode as that specified in capture-config!')
        
        # check the requested capture config matches the current receiver.
        receiver_in_capture_config = capture_config_dict['receiver'] 
        if receiver_in_capture_config != self.receiver_name:
            raise ValueError(f'Capture config receiver must match the current receiver. Got {receiver_in_capture_config} and {self.receiver_name} respectively.')
    
        print(f"Dummy capture using receiver {self.receiver_name}\nmode: {self.mode}\n")
        print(f"loading the capture-config for tag {tag}")
        json_helpers.print_config(capture_config_dict)
        print(f"\n")
        self.capture.start(self.mode, capture_config_dict)
        return
 




