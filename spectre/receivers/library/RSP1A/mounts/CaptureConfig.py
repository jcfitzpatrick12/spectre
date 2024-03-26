from spectre.receivers.CaptureConfigMount import CaptureConfigMount
from spectre.receivers.mount_register import register_capture_config_mount



@register_capture_config_mount("RSP1A")
class CaptureConfig(CaptureConfigMount):
    def __init__(self,):
        super().__init__()
        pass

    def set_templates(self):
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
            }
        }


    def set_validators(self):
        self.validators = {
            "fixed": self.fixed_validator,
            "sweeping": self.sweeping_validator
        }

    
    def fixed_validator(self, capture_config_dict):
        center_freq = capture_config_dict['center_freq']
        bandwidth = capture_config_dict['bandwidth']
        samp_rate = capture_config_dict['samp_rate']
        IF_gain = capture_config_dict['IF_gain']
        RF_gain = capture_config_dict['RF_gain']
        chunk_size = capture_config_dict['chunk_size']
        integration_time = capture_config_dict['integration_time']

        self.validate_center_freq(center_freq)
        self.validate_bandwidth(bandwidth, samp_rate)
        self.validate_samp_rate(bandwidth, samp_rate)
        self.validate_IF_gain(IF_gain)
        self.validate_RF_gain(RF_gain)
        self.validate_chunk_size(chunk_size)
        self.validate_integration_time(integration_time, chunk_size)
        pass

    def sweeping_validator(self, capture_config_dict):
        pass

    
    def validate_center_freq(self, proposed_center_freq):
        if proposed_center_freq <= 0:
            raise ValueError(f"Center frequency must be non-negative. Received {proposed_center_freq}")
        pass


    def validate_bandwidth(self, proposed_bandwidth, proposed_samp_rate):
        if proposed_samp_rate < proposed_bandwidth:
            raise ValueError(f"Sample rate must be greater than or equal to the bandwidth.")
        pass


    def validate_samp_rate(self, proposed_bandwidth, proposed_samp_rate):
        if proposed_samp_rate < proposed_bandwidth:
            raise ValueError("Sample rate must be greater than or equal to the bandwidth.")
        pass


    def validate_RF_gain(self, RF_gain):
        if RF_gain > 0:
            raise ValueError(f"RF_gain must non-positive. Received {RF_gain}.")
        pass

    def validate_IF_gain(self, IF_gain):
        if IF_gain > 0:
            raise ValueError(f"IF_gain must non-positive. Received {IF_gain}.")
        pass


    def validate_chunk_size(self, chunk_size):
        pass


    def validate_integration_time(self, integration_time, chunk_size):
        if integration_time > chunk_size:
            raise ValueError(f'Integration time cannot be greater than chunk_size.')
        pass
