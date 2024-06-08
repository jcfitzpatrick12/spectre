# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

def default_validate_window_size(window_size: int):
    if window_size < 0:
        raise ValueError(f"\"window_size\" must be strictly positive.")


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