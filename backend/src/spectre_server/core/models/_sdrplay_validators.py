# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing
import logging

from ._validators import validate_in_range, validate_one_of

_LOGGER = logging.getLogger(__name__)

SAMPLE_RATE_LOWER_BOUND = 62.5e3
SAMPLE_RATE_UPPER_BOUND = 10.66e6
CENTER_FREQUENCY_LOWER_BOUND = 1e3
CENTER_FREQUENCY_UPPER_BOUND = 2e9
IF_GAIN_UPPER_BOUND = -20
IF_GAIN_LOWER_BOUND = -59
RF_GAIN_UPPER_BOUND = 0
API_RETUNING_LATENCY = 25 * 1e-3
LOW_IF_SAMPLE_RATE_CUTOFF = 2e6
LOW_IF_PERMITTED_SAMPLE_RATES = [LOW_IF_SAMPLE_RATE_CUTOFF / (2**i) for i in range(6)]
# bandwidth == 0 means 'AUTO', i.e. the largest bandwidth compatible with the sample rate
BANDWIDTH_OPTIONS = [0, 200e3, 300e3, 600e3, 1.536e6, 5e6, 6e6, 7e6, 8e6]
LOW_IF_SAMPLE_RATE_CUTOFF = 2e6
LOW_IF_PERMITTED_SAMPLE_RATES = [LOW_IF_SAMPLE_RATE_CUTOFF / (2**i) for i in range(6)]
EXPECTED_OUTPUT_TYPES: list[str] = ["fc32", "sc16"]


def validate_center_frequency(center_frequency: float) -> None:
    validate_in_range(
        center_frequency,
        lower_bound=CENTER_FREQUENCY_LOWER_BOUND,
        upper_bound=CENTER_FREQUENCY_UPPER_BOUND,
        name="center_frequency",
    )


def validate_constant_lna_state(
    min_frequency: float,
    max_frequency: float,
    get_rf_gains: typing.Callable[[float], list[int]],
):
    if get_rf_gains(min_frequency) != get_rf_gains(max_frequency):
        _LOGGER.warning(
            "Crossing a threshold where the LNA state has to change. Performance may be reduced."
        )


def validate_sample_rate(sample_rate: float) -> None:
    validate_in_range(
        sample_rate,
        lower_bound=SAMPLE_RATE_LOWER_BOUND,
        upper_bound=SAMPLE_RATE_UPPER_BOUND,
        name="sample_rate",
    )


def validate_bandwidth(bandwidth: float) -> None:
    validate_one_of(bandwidth, BANDWIDTH_OPTIONS, name="bandwidth")


def validate_if_gain(if_gain: float) -> None:
    validate_in_range(
        if_gain,
        lower_bound=IF_GAIN_LOWER_BOUND,
        upper_bound=IF_GAIN_UPPER_BOUND,
        name="if_gain",
    )


def validate_low_if_sample_rate(sample_rate: float) -> None:
    """Validate the sample rate if the receiver is operating in low IF mode.

    The minimum physical sampling rate of the SDRplay hardware is 2 MHz. Lower effective rates can be achieved
    through decimation, as handled by the `gr-sdrplay3` OOT module. This function ensures that the sample rate
    is not silently adjusted by the backend.

    For implementation details, refer to:
    https://github.com/fventuri/gr-sdrplay3/blob/v3.11.0.9/lib/rsp_impl.cc#L140-L179
    """

    if sample_rate <= LOW_IF_SAMPLE_RATE_CUTOFF:
        if sample_rate not in LOW_IF_PERMITTED_SAMPLE_RATES:
            raise ValueError(
                f"If the requested sample rate is less than or equal to {LOW_IF_SAMPLE_RATE_CUTOFF}, "
                f"the receiver will be operating in low IF mode. "
                f"So, the sample rate must be exactly one of {LOW_IF_PERMITTED_SAMPLE_RATES}. "
                f"Got sample rate {sample_rate} Hz"
            )


def validate_rf_gain(rf_gain: float, expected_rf_gains: list[int]):
    """Validate the RF gain value against the expected values for the current LNA state.

    The RF gain is determined by the LNA state and can only take specific values as documented in the
    gain reduction tables of the SDRplay API specification.

    For implementation details, refer to the `gr-sdrplay3` OOT module:
    https://github.com/fventuri/gr-sdrplay3/blob/v3.11.0.9/lib/rsp_impl.cc#L378-L387
    """
    validate_one_of(
        rf_gain, [float(rf_gain) for rf_gain in expected_rf_gains], "rf_gain"
    )


def validate_output_type(output_type: str):
    """Checks the output type is supported."""
    validate_one_of(output_type, EXPECTED_OUTPUT_TYPES, "output_type")
