# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from scipy.signal import get_window


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


def default_validate(center_freq: float = None,
                     samp_rate: float = None,
                     bandwidth: float = None,
                     chunk_size: int = None,
                     integration_time: float = None,
                     window_type: str = None,
                     window_kwargs: dict = None,
                     window_size: int = None,
                     STFFT_kwargs: dict = None,
                     chunk_key: str = None,
                     event_handler_key: str = None,
                     watch_extension: str = None,
                     ) -> None:
    
    if not chunk_key == "default":
        raise ValueError(f"chunk_key must be specified as \"default\". Received: {chunk_key}")

    if not event_handler_key == "default":
        raise ValueError(f"event_handler_key must be specified as \"default\". Received: {event_handler_key}")
    
    if not center_freq is None:
        default_validate_center_freq(center_freq)
    
    if not samp_rate is None:
        if bandwidth is None:
            raise ValueError(f"Cannot validate samp_rate without specifying the bandwidth. Received bandwidth: {bandwidth}.")
        default_validate_samp_rate(bandwidth, samp_rate)
    
    if not chunk_size is None:
        default_validate_chunk_size(chunk_size)
    
    if not integration_time is None:
        if chunk_size is None:
            raise ValueError(f"Cannot validate integration_time without specifying chunk_size. Received chunk_size: {chunk_size}")
        default_validate_integration_time(integration_time, chunk_size)

    if not window_type is None:
        if window_kwargs is None:
            raise ValueError(f"Cannot validate window, without specifying window_kwargs. Received window_kwargs: {window_kwargs}")

        if window_size is None:
            raise ValueError(f"Cannot validate window without specifying window_size. Received: {window_size}")
        
        if chunk_size is None:
            raise ValueError(f"Cannot validate window without specifying chunk_size. Received chunk_size: {chunk_size}")
        

        if bandwidth is None:
            raise ValueError(f"Cannot validate window without specifying the samp_rate. Received bandwidth: {samp_rate}.")
        
        default_validate_window(window_type, 
                                window_kwargs, 
                                window_size,
                                chunk_size,
                                samp_rate)
    

    if not STFFT_kwargs is None:
        default_validate_STFFT_kwargs(STFFT_kwargs)
    

    if not watch_extension is None:
        default_validate_watch_extension(watch_extension)

    return
    

def is_power_of_two(n):
    return (n != 0) and (n & (n-1) == 0)


def default_validate_window(window_type: str, 
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


def default_validate_STFFT_kwargs(STFFT_kwargs: dict):
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
    

def validate_center_freq(proposed_center_freq: float):
    if proposed_center_freq <= 0:
        raise ValueError(f"Center frequency must be non-negative. Received: {proposed_center_freq}")
    return


def default_validate_center_freq(center_freq: float):
    if center_freq <= 0:
        raise ValueError(f"Center frequency must be strictly positive. Received: {center_freq}")
    return


def default_validate_bandwidth(bandwidth: float, samp_rate: int) -> None:
    if samp_rate < bandwidth:
        raise ValueError(f"Sample rate must be greater than or equal to the bandwidth.")
    return


def default_validate_samp_rate(bandwidth: float, samp_rate: int) -> None:
    if samp_rate < bandwidth:
        raise ValueError("Sample rate must be greater than or equal to the bandwidth.")
    return


def default_validate_chunk_size(chunk_size: int) -> None:
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be strictly positive. Received: {chunk_size}")
    return


def default_validate_integration_time(integration_time: int, chunk_size: int) -> None:
    if integration_time < 0:
        raise ValueError(f'integration_time must be non-negative. Received: {integration_time}')
    
    if integration_time > chunk_size:
        raise ValueError(f'integration_time must be less than or equal to chunk_size.')
    return


def default_validate_watch_extension(watch_extension: str) -> None:
    if "." in watch_extension:
        raise ValueError(f"Extension should be specified without \".\". Received: {watch_extension}")
    return