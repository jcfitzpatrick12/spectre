# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

def validate_center_freq(proposed_center_freq: float):
    if proposed_center_freq <= 0:
        raise ValueError(f"Center frequency must be non-negative. Received {proposed_center_freq}")
    return


def validate_bandwidth(proposed_bandwidth: float, proposed_samp_rate: int) -> None:
    if proposed_samp_rate < proposed_bandwidth:
        raise ValueError(f"Sample rate must be greater than or equal to the bandwidth.")
    return


def validate_samp_rate(proposed_bandwidth: float, proposed_samp_rate: int) -> None:
    if proposed_samp_rate < proposed_bandwidth:
        raise ValueError("Sample rate must be greater than or equal to the bandwidth.")
    return


def validate_RF_gain(RF_gain: int) -> None:
    if RF_gain > 0:
        raise ValueError(f"RF_gain must non-positive. Received {RF_gain}.")
    return

def validate_IF_gain(IF_gain: int) -> None:
    if IF_gain > 0:
        raise ValueError(f"IF_gain must non-positive. Received {IF_gain}.")
    return


def validate_chunk_size(chunk_size: int) -> None:
    return


def validate_integration_time(integration_time: int, chunk_size: int) -> None:
    if integration_time > chunk_size:
        raise ValueError(f'Integration time cannot be greater than chunk_size.')
    return