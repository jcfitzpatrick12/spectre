# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any

from spectre.receivers.receiver_register import register_receiver
from spectre.receivers.base import SDRPlayReceiver
from spectre.receivers.library.rsp1a.gr import fixed, sweep
from spectre.receivers import validators

@register_receiver("rsp1a")
class Receiver(SDRPlayReceiver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def _set_capture_methods(self) -> None:
        self._capture_methods = {
            "fixed": self.__fixed,
            "sweep": self.__sweep
        }
        return
    

    def _set_validators(self) -> None:
        self._validators = {
            "fixed": self.__fixed_validator,
            "sweep": self.__sweep_validator
        }
        return
    

    def _set_templates(self) -> None:
        default_fixed_template = self._get_default_template("fixed")
        default_sweep_template = self._get_default_template("sweep")
        self._templates = {
            "fixed": default_fixed_template,
            "sweep": default_sweep_template
        }


    def _set_specifications(self) -> None:
        self._specifications = {
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


    def __fixed(self, capture_configs: list[str, Any]) -> None:
        capture_config = capture_configs[0]
        fixed.main(capture_config)
    
    
    def __sweep(self, capture_configs: list[str, Any]) -> None:
        capture_config = capture_configs[0]
        sweep.main(capture_config)
    

    def __fixed_validator(self, capture_config: dict[str, Any]) -> None:
        self._default_fixed_validator(capture_config)
        self._sdrplay_validator(capture_config)
    

    def __sweep_validator(self, capture_config: dict[str, Any]) -> None:
        self._default_sweep_validator(capture_config)
        self._sdrplay_validator(capture_config)