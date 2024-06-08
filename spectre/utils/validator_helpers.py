# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from scipy.signal import get_window

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
        raise ValueError(f"chunk_key must be specified as \"default\". Received {chunk_key}")


    if not event_handler_key == "default":
        raise ValueError(f"event_handler_key must be specified as \"default\". Received {event_handler_key}")
    

    if center_freq:
        default_validate_center_freq(center_freq)
    

    if samp_rate:
        if not bandwidth:
            raise ValueError(f"Cannot validate samp_rate without specifying the bandwidth. Received bandwidth = {bandwidth}.")
        default_validate_samp_rate(bandwidth, samp_rate)
    

    if chunk_size:
        default_validate_chunk_size(chunk_size)
    

    if integration_time:
        if not chunk_size:
            raise ValueError(f"Cannot validate integration_time without specifying chunk_size. Received chunk_size = {chunk_size}")
        default_validate_integration_time(integration_time, chunk_size)


    if window_type:
        if not window_kwargs:
            raise ValueError(f"Cannot validate window_type, without specifying window_kwargs. Received window_kwargs = {window_kwargs}")

        if not window_size:
            raise ValueError(f"Cannot validate window_type without specifying window_size. Received {window_size}")
        
        default_validate_window(window_type, window_kwargs, window_size)
    

    if STFFT_kwargs:
        default_validate_STFFT_kwargs(STFFT_kwargs)
    

    if watch_extension:
        default_validate_watch_extension(watch_extension)
    

def default_validate_window(window_type: str, window_kwargs: dict, window_size: int) -> None:
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
        raise KeyError(f"\"hop\" is a required key in STFFT_kwargs. Received {STFFT_keys}.")
    
    hop_value = STFFT_kwargs.get("hop")
    hop_value_type = type(hop_value)
    if hop_value_type != int:
        raise TypeError(f"\"hop\" must be specified as an integer. Received {hop_value_type}.")
    
    if hop_value < 0:
        raise ValueError("\"hop\" must be strictly positive.")
    

def validate_center_freq(proposed_center_freq: float):
    if proposed_center_freq <= 0:
        raise ValueError(f"Center frequency must be non-negative. Received {proposed_center_freq}")


def default_validate_center_freq(center_freq: float):
    if center_freq <= 0:
        raise ValueError(f"Center frequency must be strictly positive. Received {center_freq}")
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
        raise ValueError("chunk_size must be strictly positive.")
    return


def default_validate_integration_time(integration_time: int, chunk_size: int) -> None:
    if integration_time > chunk_size:
        raise ValueError(f'Integration time cannot be greater than chunk_size.')
    return


def default_validate_watch_extension(watch_extension: str) -> None:
    if "." in watch_extension:
        raise ValueError(f"Extension should be specified without \".\". Received {watch_extension}")
    return