from spectre.receivers.CaptureConfigMount import CaptureConfigMount
from spectre.receivers.mount_register import register_capture_config_mount
from spectre.utils import validator_helpers


@register_capture_config_mount("RSP1A")
class CaptureConfig(CaptureConfigMount):
    def __init__(self,):
        super().__init__()
        pass

    def set_templates(self) -> None:
        self.templates = {
            "fixed": {
                # 'fixed_param': str,
                "center_freq": float,
                "bandwidth": float,
                "samp_rate": int, 
                "IF_gain": int,
                "RF_gain": int,
                "chunk_size": int,
                "integration_time": int,
                "data_dir": str,
            },
            'sweeping': {
                # 'sweeping_param': str,
                "center_freq": float,
                "samp_rate": int,
                "IF_gain": int,
                "RF_gain": int,
                "chunk_size": int,
                "swept_bandwidth": float,
                "frequency_step": float,
                "sweep_window": float,
                "integration_time": float,
                "data_dir": str,
            }
        }


    def set_validators(self) -> None:
        self.validators = {
            "fixed": self.fixed_validator,
            "sweeping": self.sweeping_validator
        }

    
    def fixed_validator(self, capture_config_dict: dict) -> None:
        center_freq = capture_config_dict['center_freq']
        bandwidth = capture_config_dict['bandwidth']
        samp_rate = capture_config_dict['samp_rate']
        IF_gain = capture_config_dict['IF_gain']
        RF_gain = capture_config_dict['RF_gain']
        chunk_size = capture_config_dict['chunk_size']
        integration_time = capture_config_dict['integration_time']

        validator_helpers.validate_center_freq(center_freq)
        validator_helpers.validate_bandwidth(bandwidth, samp_rate)
        validator_helpers.validate_samp_rate(bandwidth, samp_rate)
        validator_helpers.validate_IF_gain(IF_gain)
        validator_helpers.validate_RF_gain(RF_gain)
        validator_helpers.validate_chunk_size(chunk_size)
        validator_helpers.validate_integration_time(integration_time, chunk_size)
        return

    def sweeping_validator(self, capture_config_dict: dict):
        return

    