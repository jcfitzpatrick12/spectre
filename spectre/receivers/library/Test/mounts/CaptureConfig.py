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
            "cosine_signal": {
                'frequency': float,
                'samp_rate': int,
                'amplitude': float,
                'data_dir': str,
            },
        }


    def set_validators(self) -> None:
        self.validators = {
            "cosine_signal": self.cosine_validator,
        }

    
    def cosine_validator(self, capture_config_dict: dict) -> None:
        return



    