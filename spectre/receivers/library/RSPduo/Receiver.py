from spectre.receivers.receiver_register import register_receiver
from spectre.receivers.SPECTREReceiver import SPECTREReceiver
from spectre.receivers.library.RSPduo.gr import tuner_1_fixed
from spectre.utils import validator_helpers

@register_receiver("RSPduo")
class Receiver(SPECTREReceiver):
    def __init__(self, receiver_name: str, mode: str):
        super().__init__(receiver_name, mode)


    def _set_capture_methods(self) -> None:
        self.capture_methods = {
            "tuner-1-fixed": self.__tuner_1_fixed
        }
        return
    

    def _set_validators(self) -> None:
        self.validators = {
            "tuner-1-fixed": self.__tuner_1_fixed_validator
        }
        return
    

    def _set_templates(self) -> None:
        default_fixed_template = self._get_default_template("fixed")
        self.templates = {
            "tuner-1-fixed": default_fixed_template
        }


    def __tuner_1_fixed(self, capture_configs: list) -> None:
        capture_config = capture_configs[0]
        tuner_1_fixed.main(capture_config)
        return
    

    def __tuner_1_fixed_validator(self, capture_config: dict) -> None:
        self._default_fixed_validator(capture_config)
        self.__RSPduo_validator(capture_config)
        return
    

    def __RSPduo_validator(self, capture_config: dict) -> None:
        # RSPduo specific validations in single tuner mode
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

    