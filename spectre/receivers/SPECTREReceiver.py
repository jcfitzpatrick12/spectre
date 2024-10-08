# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from spectre.receivers.BaseReceiver import BaseReceiver
from spectre.receivers import validators

# optional parent class which provides default templates and validators
class SPECTREReceiver(BaseReceiver):
    def __init__(self, receiver_name: str, mode: str = None):
        self.__set_default_templates()
        super().__init__(receiver_name, mode = mode)
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
            "sweep": {
                "min_freq": float, # minimum defined frequency for the sweep
                "max_freq": float, # maximum defined frequency for the sweep
                "samples_per_step": int, # the number of samples in each step in one sweep
                "freq_step": float, # the increment in center_frequency between steps
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
            }
        }
        return
    

    def _get_default_template(self, default_template_key: str) -> dict:
        default_template = self.default_templates.get(default_template_key)
        if default_template is None:
            raise KeyError(f"No default template found with key {default_template_key}")
        return default_template
    

    # ! TO BE IMPLEMENTED ! # 
    def _default_sweep_validator(self, capture_config: dict) -> None:
        return
    

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

        validators.validate_center_freq_strictly_positive(center_freq)
        validators.validate_samp_rate_strictly_positive(samp_rate)
        validators.validate_bandwidth_strictly_positive(bandwidth)
        validators.validate_nyquist_criterion(samp_rate, bandwidth)
        validators.validate_chunk_size_strictly_positive(chunk_size)
        validators.validate_integration_time(integration_time, chunk_size) 
        validators.validate_window(window_type, 
                                          window_kwargs, 
                                          window_size,
                                          chunk_size,
                                          samp_rate)
        validators.validate_STFFT_kwargs(STFFT_kwargs)
        validators.validate_chunk_key(chunk_key, "default")
        validators.validate_event_handler_key(event_handler_key, "default")
        validators.validate_gain_is_negative(IF_gain)
        validators.validate_gain_is_negative(RF_gain)
        return