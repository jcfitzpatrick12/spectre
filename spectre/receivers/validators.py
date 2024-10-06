# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from scipy.signal import get_window
from math import floor
import warnings


def closed_upper_bound_RF_gain(RF_gain: float, RF_gain_upper_bound: float) -> None:
    if not (RF_gain <= RF_gain_upper_bound):
        raise ValueError(f"RF_gain must be strictly less than or equal to {RF_gain_upper_bound} [dB]. Got {RF_gain} [dB]")
    return


def closed_upper_bound_IF_gain(IF_gain: float, IF_gain_upper_bound: float) -> None:
    if not (IF_gain <= IF_gain_upper_bound):
        raise ValueError(f"IF_gain must be strictly less than or equal to {IF_gain_upper_bound} [dB]. Got {IF_gain} [dB]")
    return


def closed_confine_center_freq(center_freq: float, center_freq_lower_bound: float, center_freq_upper_bound: float) -> None:
    if not (center_freq_lower_bound <= center_freq <= center_freq_upper_bound):
        raise ValueError(f"center_freq must be between {center_freq_lower_bound*1e-3} [kHz] and {center_freq_upper_bound*1e-9} [GHz]. Received {center_freq*1e-6} [MHz]")
    return


def closed_confine_samp_rate(samp_rate: int, samp_rate_lower_bound: int, samp_rate_upper_bound: int) -> None:
    if not (samp_rate_lower_bound <= samp_rate <= samp_rate_upper_bound):
        raise ValueError(f"samp_rate must be between {samp_rate_lower_bound*1e-6} [MHz] and {samp_rate_upper_bound*1e-6} [MHz]. Received {samp_rate*1e-6} [MHz].")
    return


def closed_confine_bandwidth(bandwidth: float, bandwidth_lower_bound: float, bandwidth_upper_bound: float) -> None:
    if not (bandwidth_lower_bound <= bandwidth <= bandwidth_upper_bound):
        raise ValueError(f"bandwidth must be between {bandwidth_lower_bound*1e-3} [kHz] and {bandwidth_upper_bound*1e-6} [MHz]. Received {bandwidth*1e-6} [MHz]")
    return
    

def is_power_of_two(n):
    return (n != 0) and (n & (n-1) == 0)


def validate_window(window_type: str, 
                        window_kwargs: dict, 
                        window_size: int,
                        chunk_size: int,
                        samp_rate: float) -> None:
    
    if not is_power_of_two(window_size):
        raise ValueError(f"window_size must be some power of two. Received: {window_size}")
    

    if window_size*(1/samp_rate) > chunk_size:
        raise ValueError(f"Windowing interval must be strictly less than the chunk size.")
    
    try:
        window_params = (window_type, *window_kwargs.values())
        w = get_window(window_params, window_size)
    except:
        raise
    return


def validate_STFFT_kwargs(STFFT_kwargs: dict):
    if len(STFFT_kwargs) == 0:
        raise ValueError(f"STFFT_kwargs cannot be empty.")
    
    STFFT_keys = STFFT_kwargs.keys()
    if "hop" not in STFFT_keys:
        raise KeyError(f"\"hop\" is a required key in STFFT_kwargs. Received: {STFFT_keys}.")
    
    hop_value = STFFT_kwargs.get("hop")
    hop_value_type = type(hop_value)
    if hop_value_type != int:
        raise TypeError(f"\"hop\" must be specified as an integer. Received: {hop_value_type}.")
    
    if hop_value < 0:
        raise ValueError(f"\"hop\" must be strictly positive. Received: {hop_value}")
    return
    

def validate_center_freq_strictly_positive(center_freq: float):
    if center_freq <= 0:
        raise ValueError(f"Center frequency must be strictly positive. Received: {center_freq/1e6} [MHz]")
    return


def validate_bandwidth_strictly_positive(bandwidth: float) -> None:
    if bandwidth < 0:
        raise ValueError(f"Bandwidth must be non-negative. Received: {bandwidth/1e6} [MHz]")
    return


def validate_nyquist_criterion(samp_rate: int, bandwidth: float) -> None:
    if samp_rate < bandwidth:
        raise ValueError(f"Sample rate must be greater than or equal to the bandwidth.")
    return


def validate_samp_rate_strictly_positive(samp_rate: int) -> None:
    if samp_rate < 0:
        raise ValueError(f"Sample rate must be strictly positive. Received: {samp_rate}")
    return


def validate_chunk_size_strictly_positive(chunk_size: int) -> None:
    if chunk_size <= 0:
        raise ValueError(f"Chunk size must be strictly positive. Received: {chunk_size} [s]")
    return


def validate_integration_time(integration_time: int, chunk_size: int) -> None:
    if integration_time < 0:
        raise ValueError(f'Integration time must be non-negative. Received: {integration_time} [s]')
    
    if integration_time > chunk_size:
        raise ValueError(f'Integration time must be less than or equal to chunk_size.')
    return


def validate_chunk_key(chunk_key: str, expected_chunk_key: str) -> None:
    if chunk_key != expected_chunk_key:
        raise ValueError(f"Expected \"{expected_chunk_key}\" for the chunk_key, received: {chunk_key}")
    return


def validate_event_handler_key(event_handler_key: str, expected_event_handler_key: str) -> None:
    if event_handler_key != expected_event_handler_key:
        raise ValueError(f"Expected \"{expected_event_handler_key}\" for the event_handler_key, received: {event_handler_key}")
    return


def validate_gain_is_negative(gain: float) -> None:
    if gain > 0:
        raise ValueError(f"Gain must be non-positive. Received {gain} [dB]")
    

def validate_num_steps_per_sweep(min_freq: float, max_freq: float, samp_rate: int, freq_step: float) -> None:
    num_steps_per_sweep = floor((max_freq - min_freq + samp_rate/2) / freq_step)
    if num_steps_per_sweep <= 1:
        raise ValueError(f"We require more than one step per sweep. Computed {num_steps_per_sweep}.")
    

def validate_num_samples_per_step(samples_per_step: int, window_size: int) -> None:
    if window_size >= samples_per_step:
        raise ValueError(f"Window size must be strictly less than the number of samples per step. Received window size {window_size} [samples], which is more than or equal to the number of samples per step {samples_per_step}.")
    

def validate_non_overlapping_steps(freq_step: float, samp_rate: int) -> None:
    if freq_step < samp_rate:
        raise NotImplementedError(f"SPECTRE does not yet support spectral steps overlapping in frequency. Received frequency step {freq_step/1e6} [MHz] which is less than the sample rate {samp_rate} [samples/second]")


def validate_step_interval(samples_per_step: int, 
                           samp_rate: int, 
                           api_latency: float) -> None:
    step_interval = samples_per_step * 1/samp_rate # [s]
    if step_interval < api_latency:
        warnings.warn(f"The computed step interval is {step_interval} [s] is of the order of empirically derived API latency {api_latency} [ms] you may experience undefined behaviour!")