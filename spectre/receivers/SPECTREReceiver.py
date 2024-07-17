# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from spectre.receivers.BaseReceiver import BaseReceiver
from spectre.utils import validator_helpers

# optional parent class which provides default templates and validators
class SPECTREReceiver(BaseReceiver):
    def __init__(self, receiver_name: str, mode: str):
        super().__init__(receiver_name, mode)
        self.__set_default_templates()
        return
    
    def __set_default_templates(self) -> None:
        self.default_templates = {
            "fixed": {
                "center_freq": float, # center frequency for the receiver
                "bandwidth": float, # bandwidth for the receiver
                "samp_rate": int, # sample rate for the receiver
                "IF_gain": int, # intermediate frequency gain for the receiver
                "RF_gain": int, # radio frequency gain for the receiver
                'chunk_size': int, #  Size of each batched file [s]
                'integration_time': float, # time over which to average spectra in postprocessing
                'window_type': str, # window type for STFFT
                'window_kwargs': dict, # keyword arguments for window function, must be in order as in scipy documentation.
                'window_size': int, # number of samples in STFFT window
                'STFFT_kwargs': dict, # keyword arguments for the scipy STFFT class
                'chunk_key': str, # tag will map to the chunk with this key
                'event_handler_key': str, # tag will map to event handler with this key during post processing
            },
            "sweeping": {
                # tbd
            }
        }
        return
    

    def _get_default_template(self, default_template_key: str) -> dict:
        default_template = self.default_templates.get(default_template_key)
        if default_template is None:
            raise KeyError(f"No default template found with key {default_template_key}")
        return default_template
    

    def _default_fixed_validator(self, capture_config: dict) -> None:
        center_freq = capture_config['center_freq']
        bandwidth = capture_config['bandwidth']
        samp_rate = capture_config['samp_rate']
        IF_gain = capture_config['IF_gain']
        RF_gain = capture_config['RF_gain']
        chunk_size = capture_config['chunk_size']
        integration_time = capture_config['integration_time']
        window_type = capture_config['window_type']
        window_kwargs = capture_config['window_kwargs']
        window_size = capture_config['window_size']
        STFFT_kwargs = capture_config['STFFT_kwargs']
        chunk_key = capture_config['chunk_key']
        event_handler_key = capture_config['event_handler_key']

        validator_helpers.validate_center_freq_strictly_positive(center_freq)
        validator_helpers.validate_samp_rate_strictly_positive(samp_rate)
        validator_helpers.validate_bandwidth_strictly_positive(bandwidth)
        validator_helpers.validate_nyquist_criterion(samp_rate, bandwidth)
        validator_helpers.validate_chunk_size_strictly_positive(chunk_size)
        validator_helpers.validate_integration_time(integration_time, chunk_size) 
        validator_helpers.validate_window(window_type, 
                                          window_kwargs, 
                                          window_size,
                                          chunk_size,
                                          samp_rate)
        validator_helpers.validate_STFFT_kwargs(STFFT_kwargs)
        validator_helpers.validate_chunk_key(chunk_key, "default")
        validator_helpers.validate_event_handler_key(event_handler_key, "default")
        validator_helpers.validate_gain_is_negative(IF_gain)
        validator_helpers.validate_gain_is_negative(RF_gain)
        return