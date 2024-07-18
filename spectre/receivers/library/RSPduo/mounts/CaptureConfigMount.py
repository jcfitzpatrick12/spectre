# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.receivers.BaseCaptureConfigMount import BaseCaptureConfigMount
from spectre.receivers.mount_register import register_capture_config_mount
from spectre.utils import validator_helpers


@register_capture_config_mount("RSPduo")
class CaptureConfigMount(BaseCaptureConfigMount):
    def __init__(self,):
        super().__init__()
        pass

    def set_templates(self) -> None:
        self.templates = {
            "tuner-1-fixed": {
                "center_freq": float,
                "bandwidth": float,
                "samp_rate": int, 
                "IF_gain": int,
                "RF_gain": int,
                'chunk_size': int, # gr (size of each batched file) [s]
                'integration_time': float, # time over which to average spectra in postprocessing
                'window_type': str, # post_proc (window type)
                'window_kwargs': dict, # post_proc (keyword arguments for window function) must be in order as in scipy documentation.
                'window_size': int, # post_proc (number of samples for window)
                'STFFT_kwargs': dict, # post_proc (keyword arguments for STFFT)
                'chunk_key': str, # tag will map to the chunk with this key
                'event_handler_key': str, # tag will map to event handler with this key during post processing
            },
        }


    def set_validators(self) -> None:
        self.validators = {
            "tuner-1-fixed": self.tuner_1_fixed_validator,
        }

    
    def tuner_1_fixed_validator(self, capture_config: dict) -> None:
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
        

        # RSPduo specific validations in single tuner mode
        center_freq_lower_bound = 1e3 # [Hz]
        center_freq_upper_bound = 2e9 # [Hz]
        validator_helpers.closed_confine_center_freq(center_freq, center_freq_lower_bound, center_freq_upper_bound)

        samp_rate_lower_bound = 200e3 # [Hz]
        samp_rate_upper_bound = 10e6 # [Hz]
        validator_helpers.closed_confine_samp_rate(samp_rate, samp_rate_lower_bound, samp_rate_upper_bound)

        bandwidth_lower_bound = 200e3 # [Hz]
        bandwidth_upper_bound = 8e6 # [Hz]
        validator_helpers.closed_confine_bandwidth(bandwidth, bandwidth_lower_bound, bandwidth_upper_bound)

        ## make a function in validator helper BOUND IF_GAIN
        IF_gain_upper_bound = -20 # [dB]
        validator_helpers.closed_upper_bound_IF_gain(IF_gain, IF_gain_upper_bound)
        
        
        ## make a function in validator helpers BOUND RF_GAIN
        RF_gain_upper_bound = 0 # [dB]
        validator_helpers.closed_upper_bound_RF_gain(RF_gain, RF_gain_upper_bound)
        return


    