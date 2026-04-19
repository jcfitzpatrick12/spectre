# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import pydantic

import spectre_server.core.events
import spectre_server.core.flowgraphs

from ._validators import (
    skip_validator,
    validate_window_size,
    validate_in_range,
    validate_one_of,
)
from ._soapy_validators import validate_output_type

HF_FREQ_LOWER_BOUND = 10e3
HF_FREQ_UPPER_BOUND = 64e6
HF_ALLOWED_SAMPLE_RATES = [2e6, 4e6, 8e6, 16e6, 32e6, 64e6]
RF_GAIN_LOWER_BOUND = -31.5
RF_GAIN_UPPER_BOUND = 0
IF_GAIN_LOWER_BOUND = -24.583
IF_GAIN_UPPER_BOUND = 33.1409
EXPECTED_OUTPUT_TYPES: list[str] = ["fc32"]


class RX888MK2FixedCenterFrequency(
    spectre_server.core.flowgraphs.RX888MK2FixedCenterFrequencyModel,
    spectre_server.core.events.FixedCenterFrequencyModel,
):
    @pydantic.model_validator(mode="after")
    def validator(self, info: pydantic.ValidationInfo):
        if skip_validator(info):
            return self
        validate_window_size(self.window_size)
        validate_output_type(self.output_type)

        if not self.antenna_port == spectre_server.core.flowgraphs.RX888MK2Port.HF:
            raise ValueError(
                f"Only the HF port is currently supported. Got {self.antenna_port}"
            )

        validate_in_range(
            self.center_frequency,
            lower_bound=HF_FREQ_LOWER_BOUND,
            upper_bound=HF_FREQ_UPPER_BOUND,
            name="center_frequency",
        )
        validate_in_range(
            self.rf_gain,
            lower_bound=RF_GAIN_LOWER_BOUND,
            upper_bound=RF_GAIN_UPPER_BOUND,
            name="rf_gain",
        )
        validate_in_range(
            self.if_gain,
            lower_bound=IF_GAIN_LOWER_BOUND,
            upper_bound=IF_GAIN_UPPER_BOUND,
            name="if_gain",
        )
        validate_one_of(self.sample_rate, HF_ALLOWED_SAMPLE_RATES, "sample_rate")
        validate_one_of(self.output_type, EXPECTED_OUTPUT_TYPES, "output_type")
        return self
