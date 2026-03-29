# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import pydantic

import spectre_server.core.events
import spectre_server.core.flowgraphs

from ._validators import (
    skip_validator,
    validate_in_range,
    validate_window_size,
    validate_nyquist_criterion,
    validate_non_overlapping_steps,
    validate_num_steps_per_sweep,
    validate_num_samples_per_step,
)
from ._usrp_validators import (
    validate_wire_format,
    validate_output_type,
    validate_sample_rate_with_master_clock_rate,
)

SAMPLE_RATE_LOWER_BOUND = 200000
SAMPLE_RATE_UPPER_BOUND = 56000000
CENTER_FREQUENCY_LOWER_BOUND = 70000000
CENTER_FREQUENCY_UPPER_BOUND = 6000000000
BANDWIDTH_LOWER_BOUND = 200000
BANDWIDTH_UPPER_BOUND = 56000000
GAIN_LOWER_BOUND = 0
GAIN_UPPER_BOUND = 76
MASTER_CLOCK_RATE_LOWER_BOUND = 5000000
MASTER_CLOCK_RATE_UPPER_BOUND = 61440000


class B200miniFixedCenterFrequency(
    spectre_server.core.flowgraphs.USRPFixedCenterFrequencyModel,
    spectre_server.core.events.FixedCenterFrequencyModel,
):
    @pydantic.model_validator(mode="after")
    def validator(self, info: pydantic.ValidationInfo):
        if skip_validator(info):
            return self
        validate_in_range(
            self.center_frequency,
            lower_bound=CENTER_FREQUENCY_LOWER_BOUND,
            upper_bound=CENTER_FREQUENCY_UPPER_BOUND,
            name="center_frequency",
        )
        validate_in_range(
            self.bandwidth,
            lower_bound=BANDWIDTH_LOWER_BOUND,
            upper_bound=BANDWIDTH_UPPER_BOUND,
            name="bandwidth",
        )
        validate_in_range(
            self.sample_rate,
            lower_bound=SAMPLE_RATE_LOWER_BOUND,
            upper_bound=SAMPLE_RATE_UPPER_BOUND,
            name="sample_rate",
        )
        validate_in_range(
            self.gain,
            lower_bound=GAIN_LOWER_BOUND,
            upper_bound=GAIN_UPPER_BOUND,
            name="gain",
        )
        validate_in_range(
            self.master_clock_rate,
            lower_bound=MASTER_CLOCK_RATE_LOWER_BOUND,
            upper_bound=MASTER_CLOCK_RATE_UPPER_BOUND,
            name="master_clock_rate",
        )
        validate_nyquist_criterion(self.sample_rate, self.bandwidth)
        validate_window_size(self.window_size)
        validate_wire_format(self.wire_format)
        validate_output_type(self.output_type)
        validate_sample_rate_with_master_clock_rate(
            self.sample_rate, self.master_clock_rate
        )
        return self


class B200miniSweptCenterFrequency(
    spectre_server.core.flowgraphs.USRPSweptCenterFrequencyModel,
    spectre_server.core.events.SweptCenterFrequencyModel,
):
    @pydantic.model_validator(mode="after")
    def validator(self, info: pydantic.ValidationInfo):
        if skip_validator(info):
            return self
        validate_in_range(
            self.min_frequency,
            lower_bound=CENTER_FREQUENCY_LOWER_BOUND,
            upper_bound=CENTER_FREQUENCY_UPPER_BOUND,
            name="center_frequency",
        )
        validate_in_range(
            self.max_frequency,
            lower_bound=CENTER_FREQUENCY_LOWER_BOUND,
            upper_bound=CENTER_FREQUENCY_UPPER_BOUND,
            name="center_frequency",
        )
        validate_in_range(
            self.bandwidth,
            lower_bound=BANDWIDTH_LOWER_BOUND,
            upper_bound=BANDWIDTH_UPPER_BOUND,
            name="bandwidth",
        )
        validate_in_range(
            self.sample_rate,
            lower_bound=SAMPLE_RATE_LOWER_BOUND,
            upper_bound=SAMPLE_RATE_UPPER_BOUND,
            name="sample_rate",
        )
        validate_in_range(
            self.gain,
            lower_bound=GAIN_LOWER_BOUND,
            upper_bound=GAIN_UPPER_BOUND,
            name="gain",
        )
        validate_in_range(
            self.master_clock_rate,
            lower_bound=MASTER_CLOCK_RATE_LOWER_BOUND,
            upper_bound=MASTER_CLOCK_RATE_UPPER_BOUND,
            name="master_clock_rate",
        )
        validate_window_size(self.window_size)
        validate_non_overlapping_steps(self.frequency_hop, self.sample_rate)
        validate_num_samples_per_step(
            self.window_size, self.dwell_time, self.sample_rate
        )
        validate_num_steps_per_sweep(
            self.min_frequency, self.max_frequency, self.frequency_hop
        )
        validate_sample_rate_with_master_clock_rate(
            self.sample_rate, self.master_clock_rate
        )
        validate_wire_format(self.wire_format)
        validate_output_type(self.output_type)
        return self
