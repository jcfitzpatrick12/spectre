from spectre.receivers.receiver_register import register_receiver
from spectre.receivers.SPECTREReceiver import SPECTREReceiver
from spectre.receivers.library.RSP1A.gr import fixed
from spectre.utils import validator_helpers

@register_receiver("RSP1A")
class Receiver(SPECTREReceiver):
    def __init__(self, receiver_name: str, mode: str):
        super().__init__(mode)


    def _set_capture_methods(self) -> None:
        self.capture_methods = {
            "fixed": self.__fixed
        }
        return
    

    def _set_validators(self) -> None:
        self.validators = {
            "fixed": self.__fixed_validator
        }
        return
    

    def _set_templates(self) -> None:
        default_fixed_template = self._get_default_template("fixed")
        self.templates = {
            "fixed": default_fixed_template
        }


    def __fixed(self, capture_configs: list) -> None:
        capture_config = capture_configs[0]
        fixed.main(capture_config)
        return
    

    def __fixed_validator(self, capture_config: dict) -> None:
        self._default_fixed_validator(capture_config)

        # RSP1A specific validations
        center_freq_lower_bound = 1e3 # [Hz]
        center_freq_upper_bound = 2e9 # [Hz]
        validator_helpers.closed_confine_center_freq(capture_config['center_freq'], center_freq_lower_bound, center_freq_upper_bound)

        samp_rate_lower_bound = 200e3 # [Hz]
        samp_rate_upper_bound = 10e6 # [Hz]
        validator_helpers.closed_confine_samp_rate(capture_config['samp_rate'], samp_rate_lower_bound, samp_rate_upper_bound)

        bandwidth_lower_bound = 200e3 # [Hz]
        bandwidth_upper_bound = 8e6 # [Hz]
        validator_helpers.closed_confine_bandwidth(capture_config['bandwidth'], bandwidth_lower_bound, bandwidth_upper_bound)

        ## make a function in validator helper BOUND IF_GAIN
        IF_gain_upper_bound = -20 # [dB]
        validator_helpers.closed_upper_bound_IF_gain(capture_config['IF_gain'], IF_gain_upper_bound)
        
        
        ## make a function in validator helpers BOUND RF_GAIN
        RF_gain_upper_bound = 0 # [dB]
        validator_helpers.closed_upper_bound_RF_gain(capture_config['RF_gain'], RF_gain_upper_bound)
        return

    