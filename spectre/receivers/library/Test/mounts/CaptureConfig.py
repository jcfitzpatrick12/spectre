from spectre.receivers.CaptureConfigMount import CaptureConfigMount
from spectre.receivers.mount_register import register_capture_config_mount
from spectre.utils import validator_helpers
from spectre.utils import dict_helpers


@register_capture_config_mount("Test")
class CaptureConfig(CaptureConfigMount):
    def __init__(self,):
        super().__init__()
        pass

    def set_templates(self) -> None:
        self.templates = {
            "cosine_signal": {
                'samp_rate': int, # gr (sampling rate)
                'frequency': float, # gr (frequency of the cosine signal)
                'amplitude': float, # gr (ampltude of the cosine signal)
                'chunks_dir': str, # gr (directory where the chunks are stored)
                'chunk_size': int, # gr (size of each batched file) [s]
                'window_type': str, # post_proc (window type)
                'window_kwargs': dict, # post_proc (keyword arguments for window function) must be in order as in scipy documentation.
                'Nx': int, # post_proc (number of samples for window)
                'STFFT_kwargs': dict, # post_proc (keyword arguments for STFFT)
                'chunk_key': str, # tag will map to the chunk with this key
                'event_handler_key': str, # tag will map to event handler with this key during post processing
                'watch_extension': str # postprocessing will call proc defined in event handler for files appearing with this extension
            },
            
            "key_value_test": {
                'int_key': int,
                'str_key': str,
                'dict_key': dict,
                'float_key': float,
                'bool_key': bool, 
            }
        }


    def set_validators(self) -> None:
        self.validators = {
            "cosine_signal": self.cosine_validator,
            "key_value_test": self.key_value_test_validator,
        }

    
    def cosine_validator(self, capture_config_dict: dict) -> None:
        return

    
    def key_value_test_validator(self, capture_config_dict: dict) -> None:
        print("Performing key value test.")
        template = self.templates.get('key_value_test')
        if template is None:
            raise ValueError("Could not find template for the key value test.")
        
        dict_helpers.validate_keys(capture_config_dict, template)
        print("Keys verified.")

        dict_helpers.validate_types(capture_config_dict, template)
        print("Values verified.")

        print("Validated capture config is consistent with the template")
        return


    