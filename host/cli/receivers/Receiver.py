from cli.utils import param_helpers, json_helpers
from cli.cfg.CaptureConfig import CaptureConfig
from cli.receivers import fetch

from cli.utils.raw_validation import validate_raw_dict


class Receiver:
    def __init__(self, receiver_name):
        self.receiver_name = receiver_name
        self.mode = None
        self.templates = fetch.fetch_templates(receiver_name)
        self.validators = fetch.fetch_validators(receiver_name)

        if self.templates.keys() != self.validators.keys():
            raise ValueError(f"Key mismatch between templates and validators for {self.receiver_name}!")
        
        self.valid_modes = list(self.templates.keys())


    def set_mode(self, mode):
        if mode not in self.valid_modes:
            raise ValueError(f'{mode} is not a defined mode for {self.receiver_name}. Need one of {self.valid_modes}')
        self.mode = mode


    def get_mode(self,):
        return self.mode
    

    def get_template(self, mode):
        if self.mode not in self.valid_modes:
            raise ValueError(f'Mode must be specified. Received {mode}.')
        return self.templates[mode]
    
    def get_validator(self, mode):
        if self.mode not in self.valid_modes:
            raise ValueError(f'Mode must be specified. Received {mode}.')
        return self.validators[mode]

    def capture(self, tag):
        if self.mode not in self.valid_modes:
            raise ValueError(f'Mode must be specified. Received {self.mode}.')
        capture_config = CaptureConfig(tag)
        capture_config_dict = capture_config.load_as_dict()
        print(f"Dummy capture using receiver {self.receiver_name}\nmode: {self.mode}\n")
        print(f"loading the capture-config for tag {tag}")
        json_helpers.print_config(capture_config_dict)
        return

    # save params to file as a capture config with tag [tag], validated according to the receiver in mode [mode]
    def save_capture_config(self, params, tag):
        # convert the user defined params to a raw_dict [key=string_value]
        raw_dict = param_helpers.params_to_raw_dict(params)
        # extract the capture config template for the current mode of the receiver
        template = self.get_template(self.mode)
        # validate the raw dict against the template
        validate_raw_dict(raw_dict, template)
        # convert the raw dict string values to those defined in the template
        capture_config_dict = param_helpers.convert_types(raw_dict, template)  
        # extract the validator function for the current mode.
        validate_capture_config = self.get_validator(self.mode)
        # validate according to receiver-specific constraints
        validate_capture_config(capture_config_dict)

        # add two extra key values to specify the mode and the receiver name for the capture config
        capture_config_dict['receiver'] = self.receiver_name
        capture_config_dict['mode'] = self.mode
        # instantiate capture_config and save the newly construcd config_dict
        capture_config = CaptureConfig(tag)
        # save to file under the requested tag
        capture_config.save_dict_as_json(capture_config_dict)
        pass    




