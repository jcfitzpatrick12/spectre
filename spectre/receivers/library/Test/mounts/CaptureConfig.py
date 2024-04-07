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
                'samp_rate': int, # gr (sampling rate)
                'frequency': float, # gr (frequency of the cosine signal)
                'amplitude': float, # gr (ampltude of the cosine signal)
                'chunks_dir': str, # gr (directory where the chunks are stored)
                'chunk_size': int, # gr (size of each batched file) [s]
                'window_type': str, # post_proc (window type)
                'window_kwargs': dict, # post_proc (keyword arguments for window function) must be in order as in scipy documentation.
                'Nx': int, # post_proc (number of samples for window)
                'STFFT_kwargs': dict # post_proc (keyword arguments for STFFT)
            },
        }


    def set_validators(self) -> None:
        self.validators = {
            "cosine_signal": self.cosine_validator,
        }

    
    def cosine_validator(self, capture_config_dict: dict) -> None:
        return



    