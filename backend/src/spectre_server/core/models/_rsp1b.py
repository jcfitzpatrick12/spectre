# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import pydantic

import spectre_server.core.events
import spectre_server.core.flowgraphs

from ._validators import (
    skip_validator,
    validate_window_size,
    validate_window_type,
    validate_nyquist_criterion,
)
from ._sdrplay_validators import (
    validate_bandwidth,
    validate_center_frequency,
    validate_if_gain,
    validate_low_if_sample_rate,
    validate_rf_gain,
    validate_sample_rate,
    validate_output_type,
)


def _get_rf_gains(center_frequency: float) -> list[int]:
    if center_frequency <= 50e6:
        return [0, -6, -12, -18, -37, -42, -61]
    elif center_frequency <= 60e6:
        return [0, -6, -12, -18, -20, -26, -32, -38, -57, -62]
    elif center_frequency <= 420e6:
        return [0, -6, -12, -18, -20, -26, -32, -38, -57, -62]
    elif center_frequency <= 1000e6:
        return [0, -7, -13, -19, -20, -27, -33, -39, -45, -64]
    elif center_frequency <= 2000e6:
        return [0, -6, -12, -20, -26, -32, -38, -43, -62]
    else:
        return []


class RSP1BFixedCenterFrequency(
    spectre_server.core.flowgraphs.RSP1BFixedCenterFrequencyModel,
    spectre_server.core.events.FixedCenterFrequencyModel,
):
    @pydantic.model_validator(mode="after")
    def validator(self, info: pydantic.ValidationInfo):
        if skip_validator(info):
            return self
        validate_nyquist_criterion(self.sample_rate, self.bandwidth)
        validate_center_frequency(self.center_frequency)
        validate_window_size(self.window_size)
        validate_window_type(self.window_type)
        validate_sample_rate(self.sample_rate)
        validate_bandwidth(self.bandwidth)
        validate_if_gain(self.if_gain)
        validate_output_type(self.output_type)
        validate_low_if_sample_rate(self.sample_rate)
        validate_rf_gain(self.rf_gain, _get_rf_gains(self.center_frequency))
        return self
