# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import pydantic

import spectre_server.core.events
import spectre_server.core.flowgraphs

from ._validators import (
    skip_validator,
    validate_window_size,
    validate_nyquist_criterion,
    validate_one_of,
    validate_in_range,
)

CENTER_FREQUENCY_LOWER_BOUND = 1e6
CENTER_FREQUENCY_UPPER_BOUND = 6e9
SAMPLE_RATE_LOWER_BOUND = 1e6
SAMPLE_RATE_UPPER_BOUND = 20e6
LNA_GAIN_LOWER_BOUND = 0
LNA_GAIN_UPPER_BOUND = 40
VGA_GAIN_LOWER_BOUND = 0
VGA_GAIN_UPPER_BOUND = 62
ALLOWED_BANDWIDTHS = [
    1e6,
    2e6,
    3e6,
    4e6,
    5e6,
    6e6,
    7e6,
    8e6,
    9e6,
    10e6,
    11e6,
    12e6,
    13e6,
    14e6,
    15e6,
    16e6,
    17e6,
    18e6,
    19e6,
    20e6,
]


class HackRFOneFixedCenterFrequency(
    spectre_server.core.flowgraphs.HackRFFixedCenterFrequencyModel,
    spectre_server.core.events.FixedCenterFrequencyModel,
):
    @pydantic.model_validator(mode="after")
    def validator(self, info: pydantic.ValidationInfo):
        if skip_validator(info):
            return self
        validate_nyquist_criterion(self.sample_rate, self.bandwidth)
        validate_window_size(self.window_size)
        validate_in_range(
            self.center_frequency,
            lower_bound=CENTER_FREQUENCY_LOWER_BOUND,
            upper_bound=CENTER_FREQUENCY_UPPER_BOUND,
            name="center_frequency",
        )
        validate_in_range(
            self.sample_rate,
            lower_bound=SAMPLE_RATE_LOWER_BOUND,
            upper_bound=SAMPLE_RATE_UPPER_BOUND,
            name="center_frequency",
        )
        validate_in_range(
            self.lna_gain,
            lower_bound=LNA_GAIN_LOWER_BOUND,
            upper_bound=LNA_GAIN_UPPER_BOUND,
            name="lna_gain",
        )
        validate_in_range(
            self.vga_gain,
            lower_bound=VGA_GAIN_LOWER_BOUND,
            upper_bound=VGA_GAIN_UPPER_BOUND,
            name="vga_gain",
        )
        validate_one_of(self.bandwidth, ALLOWED_BANDWIDTHS, "bandwidth")
        return self
