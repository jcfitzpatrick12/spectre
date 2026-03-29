# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing
import math

import pydantic

import spectre_server.core.fields


def skip_validator(info: pydantic.ValidationInfo) -> bool:
    return True if info.context and info.context.get("skip", False) else False


T = typing.TypeVar("T")


def validate_one_of(
    value: T,
    options: list[T],
    name: str = "Value",
):
    """
    Validate that the input value is one of a list of pre-defined options.

    :param value: The value to validate.
    :param options: The list of allowed options.
    :param name: The name of the value being validated (for error messages).
    :raises ValueError: If the value is not one of the options.
    """
    if value not in options:
        raise ValueError(f"{name} must be one of {options}. Got {value}.")


def validate_in_range(
    value: float | int,
    lower_bound: typing.Optional[float | int] = None,
    upper_bound: typing.Optional[float | int] | None = None,
    strict_lower: bool = False,
    strict_upper: bool = False,
    name: str = "Value",
) -> None:
    """
    Validate that a numeric value is within a specified interval.

    :param value: The value to validate.
    :param lower_bound: The value must be greater than `lower_bound`. Inclusive if `strict_lower` is False.
    :param upper_bound: The value must be less than `upper_bound`. Inclusive if `strict_upper` is False.
    :param strict_lower: If true, the value must be strictly greater than `lower_bound`.
    :param strict_upper: If true, the value must be strictly less than `upper_bound`.
    :param name: Include the name of the value being validated in the error message.
    :raises ValueError: If the value is outside the specified interval.
    """
    if lower_bound is not None:
        if strict_lower and value <= lower_bound:
            raise ValueError(
                f"{name} must be strictly greater than {lower_bound}. Got {value}."
            )
        if not strict_lower and value < lower_bound:
            raise ValueError(
                f"{name} must be greater than or equal to {lower_bound}. Got {value}."
            )

    if upper_bound is not None:
        if strict_upper and value >= upper_bound:
            raise ValueError(
                f"{name} must be strictly less than {upper_bound}. Got {value}."
            )
        if not strict_upper and value > upper_bound:
            raise ValueError(
                f"{name} must be less than or equal to {upper_bound}. Got {value}."
            )


def validate_window_size(window_size: int):
    """Check that the window size is a power of two."""
    if window_size & (window_size - 1) != 0:
        raise ValueError("The window size must be a power of 2")


def validate_window_type(window_type: str):
    """Check that the window is supported."""
    expected_window_types = [
        spectre_server.core.fields.WindowType.BLACKMAN,
        spectre_server.core.fields.WindowType.HANN,
        spectre_server.core.fields.WindowType.BOXCAR,
    ]
    if window_type not in expected_window_types:
        raise ValueError(
            f"{window_type} not supported. Expected one of {expected_window_types}"
        )


def validate_nyquist_criterion(sample_rate: float, bandwidth: float) -> None:
    """Ensure that the Nyquist criterion is satisfied."""
    if sample_rate < bandwidth:
        raise ValueError(
            (
                f"Nyquist criterion has not been satisfied. "
                f"Sample rate must be greater than or equal to the bandwidth. "
                f"Got sample rate {sample_rate} [Hz], and bandwidth {bandwidth} [Hz]"
            )
        )


def validate_non_overlapping_steps(frequency_hop: float, sample_rate: float) -> None:
    """Ensure that the stepped spectrograms are non-overlapping in the frequency domain."""

    if frequency_hop < sample_rate:
        raise NotImplementedError(
            f"Spectre does not yet support spectral steps overlapping in frequency. "
            f"Got frequency hop {frequency_hop * 1e-6} [MHz] which is less than the sample "
            f"rate {sample_rate * 1e-6} [MHz]"
        )


def validate_num_steps_per_sweep(
    min_frequency: float, max_frequency: float, frequency_hop: float
) -> None:
    """Ensure that there are at least two steps in frequency per sweep."""

    num_steps_per_sweep = math.floor((max_frequency - min_frequency) / frequency_hop)
    if num_steps_per_sweep <= 1:
        raise ValueError(
            (
                f"We need strictly greater than one step per sweep. "
                f"Computed {num_steps_per_sweep} step per sweep"
            )
        )


def validate_num_samples_per_step(
    window_size: int, dwell_time: float, sample_rate: float
) -> None:
    """Ensure that the number of samples per step is greater than the window size."""
    num_samples_per_step = dwell_time * sample_rate
    if window_size >= num_samples_per_step:
        raise ValueError(
            (
                f"Window size must be strictly less than the number of samples per step. "
                f"Got window size {window_size}, which is more than or equal "
                f"to the number of samples per step {num_samples_per_step}. "
                f"Please increase the dwell time."
            )
        )
