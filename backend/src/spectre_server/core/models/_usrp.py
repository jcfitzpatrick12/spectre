# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import pydantic

import spectre_server.core.events
import spectre_server.core.flowgraphs

from ._validators import (
    skip_validator,
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


class USRPFixedCenterFrequency(
    spectre_server.core.flowgraphs.USRPFixedCenterFrequencyModel,
    spectre_server.core.events.FixedCenterFrequencyModel,
):
    @pydantic.model_validator(mode="after")
    def validator(self, info: pydantic.ValidationInfo):
        if skip_validator(info):
            return self
        validate_nyquist_criterion(self.sample_rate, self.bandwidth)
        validate_window_size(self.window_size)
        validate_wire_format(self.wire_format)
        validate_output_type(self.output_type)
        validate_sample_rate_with_master_clock_rate(
            self.sample_rate, self.master_clock_rate
        )
        return self


class USRPSweptCenterFrequency(
    spectre_server.core.flowgraphs.USRPSweptCenterFrequencyModel,
    spectre_server.core.events.SweptCenterFrequencyModel,
):
    @pydantic.model_validator(mode="after")
    def validator(self, info: pydantic.ValidationInfo):
        if skip_validator(info):
            return self
        validate_window_size(self.window_size)
        validate_non_overlapping_steps(self.frequency_hop, self.sample_rate)
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
