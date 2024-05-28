from spectre.receivers.BaseCaptureConfigMount import BaseCaptureConfigMount
from spectre.receivers.mount_register import register_capture_config_mount
from spectre.utils import validator_helpers


@register_capture_config_mount("RSPDuo")
class CaptureConfigMount(BaseCaptureConfigMount):
    def __init__(self,):
        super().__init__()
        pass

    def set_templates(self) -> None:
        self.templates = {
            "tuner_1_fixed": {
                "center_freq": float,
                "bandwidth": float,
                "samp_rate": int, 
                "IF_gain": int,
                "RF_gain": int,
                'chunk_size': int, # gr (size of each batched file) [s]
                'window_type': str, # post_proc (window type)
                'window_kwargs': dict, # post_proc (keyword arguments for window function) must be in order as in scipy documentation.
                'Nx': int, # post_proc (number of samples for window)
                'STFFT_kwargs': dict, # post_proc (keyword arguments for STFFT)
                'chunk_key': str, # tag will map to the chunk with this key
                'event_handler_key': str, # tag will map to event handler with this key during post processing
                'watch_extension': str, # postprocessing will call proc defined in event handler for files appearing with this extension
                'integration_time': float # time over which to average spectra in postprocessing
            },
        }


    def set_validators(self) -> None:
        self.validators = {
            "tuner_1_fixed": self.tuner_1_fixed_validator,
        }

    
    def tuner_1_fixed_validator(self, capture_config: dict) -> None:
        center_freq = capture_config['center_freq']
        bandwidth = capture_config['bandwidth']
        samp_rate = capture_config['samp_rate']
        IF_gain = capture_config['IF_gain']
        RF_gain = capture_config['RF_gain']
        chunk_size = capture_config['chunk_size']

        validator_helpers.validate_center_freq(center_freq)
        validator_helpers.validate_bandwidth(bandwidth, samp_rate)
        validator_helpers.validate_samp_rate(bandwidth, samp_rate)
        validator_helpers.validate_IF_gain(IF_gain)
        validator_helpers.validate_RF_gain(RF_gain)
        validator_helpers.validate_chunk_size(chunk_size)
        return


    