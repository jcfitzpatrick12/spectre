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
            "tuner_1_fixed": {
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
                'watch_extension': str, # postprocessing will call proc defined in event handler for files appearing with this extension
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
        integration_time = capture_config['integration_time']
        window_type = capture_config['window_type']
        window_kwargs = capture_config['window_kwargs']
        window_size = capture_config['window_size']
        STFFT_kwargs = capture_config['STFFT_kwargs']
        chunk_key = capture_config['chunk_key']
        event_handler_key = capture_config['event_handler_key']
        watch_extension = capture_config['watch_extension']

        # do default validations
        validator_helpers.default_validate(center_freq = center_freq,
                                           samp_rate = samp_rate,
                                           bandwidth = bandwidth,
                                           chunk_size = chunk_size,
                                           integration_time = integration_time,
                                           window_type = window_type,
                                           window_kwargs = window_kwargs,
                                           window_size = window_size,
                                           STFFT_kwargs = STFFT_kwargs,
                                           chunk_key = chunk_key,
                                           event_handler_key = event_handler_key,
                                           watch_extension = watch_extension
                                           )
        

        # RSPduo specific validations in single tuner mode
        center_freq_lower_bound = 1e3 # [Hz]
        center_freq_upper_bound = 2e9 # [Hz]
        if not (center_freq_lower_bound <= center_freq <= center_freq_upper_bound):
            raise ValueError(f"center_freq must be between {center_freq_lower_bound*1e-3} [kHz] and {center_freq_upper_bound*1e-9} [GHz]. Received {center_freq*1e-6} [MHz]")

        samp_rate_lower_bound = 2e6 # [Hz]
        samp_rate_upper_bound = 10e6 # [Hz]
        if not (samp_rate_lower_bound <= samp_rate <= samp_rate_upper_bound):
            raise ValueError(f"samp_rate must be between {samp_rate_lower_bound*1e-6} [MHz] and {samp_rate_upper_bound*1e-6} [MHz]. Received {samp_rate*1e-6} [MHz].")

        bandwidth_lower_bound = 200e3 # [Hz]
        bandwidth_upper_bound = 8e6 # [Hz]
        if not (bandwidth_lower_bound <= bandwidth <= bandwidth_upper_bound):
            raise ValueError(f"bandiwdth must be between {bandwidth_lower_bound*1e-3} [kHz] and {8*1e-6} [MHz]. Received {bandwidth*1e-6} [MHz]")
        
        IF_gain_upper_bound = -20 # [dB]
        if not (IF_gain <= IF_gain_upper_bound):
            raise ValueError(f"IF_gain must be strictly less than or equal to -20 [dB]. Got {IF_gain} [dB]")

        RF_gain_lower_bound = 0 # [dB]
        if not (RF_gain <= RF_gain_lower_bound):
            raise ValueError(f"RF_gain must be strictly less than or equal to 0 [dB]. Got {RF_gain} [dB]")
        return


    