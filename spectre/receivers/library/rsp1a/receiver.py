# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.receivers.receiver_register import register_receiver
from spectre.receivers.base import SDRPlayReceiver
from spectre.receivers.library.rsp1a.gr import fixed, sweep
from spectre.receivers import validators

@register_receiver("RSP1A")
class Receiver(SDRPlayReceiver):
    def __init__(self, receiver_name: str, mode: str = None):
        super().__init__(receiver_name, mode = mode)


    def _set_capture_methods(self) -> None:
        self.capture_methods = {
            "fixed": self.__fixed,
            "sweep": self.__sweep
        }
        return
    

    def _set_validators(self) -> None:
        self.validators = {
            "fixed": self.__fixed_validator,
            "sweep": self.__sweep_validator
        }
        return
    

    def _set_templates(self) -> None:
        default_fixed_template = self._get_default_template("fixed")
        default_sweep_template = self._get_default_template("sweep")
        self.templates = {
            "fixed": default_fixed_template,
            "sweep": default_sweep_template
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


    def __fixed(self, capture_configs: list) -> None:
        capture_config = capture_configs[0]
        fixed.main(capture_config)
        return
    
    
    def __sweep(self, capture_configs: list) -> None:
        capture_config = capture_configs[0]
        sweep.main(capture_config)
        return
    

    def __fixed_validator(self, capture_config: dict) -> None:
        self._default_fixed_validator(capture_config)
        self._sdrplay_validator(capture_config)
        return
    

    def __sweep_validator(self, capture_config: dict) -> None:
        self._default_sweep_validator(capture_config)
        self._sdrplay_validator(capture_config)
        return
    

    
    def __RSP1A_validator(self, capture_config: dict) -> None:
        # RSP1A specific validations
        center_freq_lower_bound = 1e3 # [Hz]
        center_freq_upper_bound = 2e9 # [Hz]
        center_freq = capture_config.get("center_freq")
        min_freq = capture_config.get("min_freq")
        max_freq = capture_config.get("max_freq")
        if center_freq:
            validators.closed_confine_center_freq(center_freq, center_freq_lower_bound, center_freq_upper_bound)
        if min_freq:
            validators.closed_confine_center_freq(min_freq, center_freq_lower_bound, center_freq_upper_bound)
        if max_freq:
            validators.closed_confine_center_freq(max_freq, center_freq_lower_bound, center_freq_upper_bound)

        samp_rate_lower_bound = 200e3 # [Hz]
        samp_rate_upper_bound = 10e6 # [Hz]
        validators.closed_confine_samp_rate(capture_config['samp_rate'], samp_rate_lower_bound, samp_rate_upper_bound)

        bandwidth_lower_bound = 200e3 # [Hz]
        bandwidth_upper_bound = 8e6 # [Hz]
        validators.closed_confine_bandwidth(capture_config['bandwidth'], bandwidth_lower_bound, bandwidth_upper_bound)

        IF_gain_upper_bound = -20 # [dB]
        validators.closed_upper_bound_IF_gain(capture_config['IF_gain'], IF_gain_upper_bound)
        
        RF_gain_upper_bound = 0 # [dB]
        validators.closed_upper_bound_RF_gain(capture_config['RF_gain'], RF_gain_upper_bound)
        return

    