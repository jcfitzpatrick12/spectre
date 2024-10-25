# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any

from spectre.receivers.receiver_register import register_receiver
from spectre.receivers.base import SPECTREReceiver
from spectre.receivers.library.test.gr import cosine_signal_1
from spectre.receivers.library.test.gr import tagged_staircase
from spectre.receivers import validators


@register_receiver("test")
class Receiver(SPECTREReceiver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def _set_capture_methods(self) -> None:
        self._capture_methods = {
            "cosine-signal-1": self.__cosine_signal_1,
            "tagged-staircase": self.__tagged_staircase
        }
    

    def _set_validators(self) -> None:
        self._validators = {
            "cosine-signal-1": self.__cosine_signal_1_validator,
            "tagged-staircase": self.__tagged_staircase_validator
        }
    

    def _set_templates(self) -> None:
        self._templates = {
            "cosine-signal-1": {
                'samp_rate': int, # [Hz]
                'frequency': float, # [Hz]
                'amplitude': float, # unitless
                'chunk_size': int, # [s]
                'time_resolution': float, # [s]
                'frequency_resolution': float, # [Hz]
                'window_type': str, # the window type for the STFFT
                'window_kwargs': dict, # keyword arguments for scipy get window function. Must be in order as in scipy documentation.
                'window_size': int, # number of samples for the window
                'STFFT_kwargs': dict, # keyword arguments for scipy STFFT class
                'chunk_key': str, # tag will map to the chunk with this key
                'event_handler_key': str # tag will map to event handler with this key during post processing
            },
            "tagged-staircase": {
                'samp_rate': int, # [Hz]
                'min_samples_per_step': int, # the size of the smallest step (in samples)
                'max_samples_per_step': int, # the size of the largest step (in samples)
                'step_increment': int, # the "height" of each step, in terms of the tagged staircase output.
                'chunk_size': int, # [s]
                'time_resolution': float, # [s]
                'frequency_resolution': float, # [Hz]
                'window_type': str, # the window type for the STFFT
                'window_kwargs': dict, # keyword arguments for scipy get window function. Must be in order as in scipy documentation.
                'window_size': int, # number of samples for the window
                'STFFT_kwargs': dict, # keyword arguments for scipy STFFT class
                'chunk_key': str, # tag will map to the chunk with this key
                'event_handler_key': str, # tag will map to event handler with this key during post processing
            }
        }
    
    def _set_specifications(self) -> None:
        self._specifications = {
        } 


    def __cosine_signal_1(self, capture_configs: list[str, Any]) -> None:
        capture_config = capture_configs[0]
        cosine_signal_1.main(capture_config)
    

    def __tagged_staircase(self, capture_configs: list[str, Any]) -> None:
        capture_config = capture_configs[0]
        tagged_staircase.main(capture_config)
    

    def __cosine_signal_1_validator(self, capture_config: dict[str, Any]) -> None:
        # unpack the capture config
        samp_rate = capture_config["samp_rate"]
        frequency = capture_config["frequency"]
        amplitude = capture_config["amplitude"]
        chunk_size = capture_config["chunk_size"]
        window_type = capture_config["window_type"]
        window_size = capture_config["window_size"]
        STFFT_kwargs = capture_config["STFFT_kwargs"]
        chunk_key = capture_config["chunk_key"]
        event_handler_key = capture_config["event_handler_key"]
        time_resolution = capture_config["time_resolution"]
        frequency_resolution = capture_config["frequency_resolution"]

        validators.validate_samp_rate_strictly_positive(samp_rate)
        validators.validate_chunk_size_strictly_positive(chunk_size)
        validators.validate_time_resolution(time_resolution, chunk_size) 
        validators.validate_window(window_type, 
                                          {}, 
                                          window_size,
                                          chunk_size,
                                          samp_rate)
        validators.validate_STFFT_kwargs(STFFT_kwargs)
        validators.validate_chunk_key(chunk_key, "fixed")
        validators.validate_event_handler_key(event_handler_key, "fixed")

        if time_resolution != 0:
            raise ValueError(f"Time resolution must be zero. Received: {time_resolution}")
        
        if frequency_resolution != 0:
            raise ValueError(f"Frequency resolution must be zero. Received {frequency_resolution}")
        
        # check that the sample rate is an integer multiple of the underlying signal frequency
        if samp_rate % frequency != 0:
            raise ValueError("samp_rate must be some integer multiple of frequency")

        a = samp_rate/frequency
        if a < 2:
            raise ValueError(f"The ratio samp_rate/frequency must be a natural number greater than two.  Received: {a}")
        
        # ensuring the window type is rectangular
        if window_type != "boxcar":
            raise ValueError(f"Window type must be \"boxcar\". Received: {window_type}")
        
        # analytical requirement
        # if p is the number of sampled cycles, we can find that p = window_size / a
        # the number of sampled cycles must be a positive natural number.
        p = window_size / a
        if window_size % a != 0:
            raise ValueError(f"The number of sampled cycles must be a positive natural number. Computed that p={p}")
    
    
        if amplitude <= 0:
            raise ValueError(f"amplitude must be strictly positive. Received: {amplitude}")
    

    def __tagged_staircase_validator(self, capture_config: dict[str, Any]) -> None:
        samp_rate = capture_config["samp_rate"]
        min_samples_per_step = capture_config["min_samples_per_step"]
        max_samples_per_step = capture_config["max_samples_per_step"]
        step_increment = capture_config["step_increment"]
        chunk_size = capture_config["chunk_size"]
        window_type = capture_config["window_type"]
        window_kwargs = capture_config["window_kwargs"]
        window_size = capture_config["window_size"]
        STFFT_kwargs = capture_config["STFFT_kwargs"]
        chunk_key = capture_config["chunk_key"]
        event_handler_key = capture_config["event_handler_key"]
        time_resolution = capture_config["time_resolution"]

        validators.validate_samp_rate_strictly_positive(samp_rate)
        validators.validate_chunk_size_strictly_positive(chunk_size)
        validators.validate_time_resolution(time_resolution, chunk_size)
        validators.validate_window(window_type, window_kwargs, window_size, chunk_size, samp_rate)
        validators.validate_STFFT_kwargs(STFFT_kwargs)
        validators.validate_chunk_key(chunk_key, "sweep")
        validators.validate_event_handler_key(event_handler_key, "sweep")

        if min_samples_per_step <= 0:
            raise ValueError(f"min_samples_per_step must be strictly positive. Received: {min_samples_per_step}")
        if max_samples_per_step <= 0:
            raise ValueError(f"max_samples_per_step must be strictly positive. Received: {max_samples_per_step}")
        if step_increment <= 0:
            raise ValueError(f"step_increment must be strictly positive. Received: {step_increment}")
        if min_samples_per_step > max_samples_per_step:
            raise ValueError(f"min_samples_per_step cannot be greater than max_samples_per_step. Received: {min_samples_per_step} > {max_samples_per_step}")
