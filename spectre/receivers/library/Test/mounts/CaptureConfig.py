from spectre.receivers.CaptureConfigMount import CaptureConfigMount
from spectre.receivers.mount_register import register_capture_config_mount
from spectre.utils import validator_helpers


@register_capture_config_mount("Test")
class CaptureConfig(CaptureConfigMount):
    def __init__(self,):
        super().__init__()
        pass

    def set_templates(self) -> None:
        self.templates = {
            "fixed": {
                'str_key': str,
                'int_key': int,
                'float_key': float,
                'bool_key': bool,
            },
        }


    def set_validators(self) -> None:
        self.validators = {
            "fixed": self.fixed_validator,
        }

    
    def fixed_validator(self, capture_config_dict: dict) -> None:
        return



    