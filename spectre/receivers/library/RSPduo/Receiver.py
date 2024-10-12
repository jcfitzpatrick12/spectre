# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.receivers.receiver_register import register_receiver
from spectre.receivers.SDRPlayReceiver import SDRPlayReceiver
from spectre.receivers.library.RSPduo.gr import tuner_1_fixed, tuner_1_sweep
from spectre.receivers import validators

@register_receiver("RSPduo")
class Receiver(SDRPlayReceiver):
    def __init__(self, receiver_name: str, mode: str = None):
        super().__init__(receiver_name, mode = mode)


    def _set_capture_methods(self) -> None:
        self.capture_methods = {
            "tuner-1-fixed": self.__tuner_1_fixed,
            "tuner-1-sweep": self.__tuner_1_sweep
        }
        return
    

    def _set_validators(self) -> None:
        self.validators = {
            "tuner-1-fixed": self.__tuner_1_fixed_validator,
            "tuner-1-sweep": self.__tuner_1_sweep_validator
        }
        return
    

    def _set_templates(self) -> None:
        self.templates = {
            "tuner-1-fixed": self._get_default_template("fixed"),
            "tuner-1-sweep": self._get_default_template("sweep"),
        }

    def _set_specifications(self) -> None:
        self.specifications = {
            "center_freq_lower_bound": 1e3, # [Hz]
            "center_freq_upper_bound": 2e9, # [Hz]
            "samp_rate_lower_bound": 200e3, # [Hz]
            "samp_rate_upper_bound": 10e6, # [Hz]
            "bandwidth_lower_bound": 200e3, # [Hz]
            "bandwidth_upper_bound": 8e6, # [Hz]
            "IF_gain_upper_bound": -20, # [dB]
            "RF_gain_upper_bound": 0, # [dB]
            "api_latency": 50 * 1e-3 # [s]
        }


    def __tuner_1_fixed(self, capture_configs: list) -> None:
        capture_config = capture_configs[0]
        tuner_1_fixed.main(capture_config)
        return
    

    def __tuner_1_sweep(self, capture_configs: list) -> None:
        capture_config = capture_configs[0]
        tuner_1_sweep.main(capture_config)
        return
    

    def __tuner_1_fixed_validator(self, capture_config: dict) -> None:
        self._default_fixed_validator(capture_config)
        self._sdrplay_validator(capture_config)
        return
    
    
    def __tuner_1_sweep_validator(self, capture_config: dict) -> None:
        self._default_sweep_validator(capture_config)
        self._sdrplay_validator(capture_config)
        return
    
