# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import pydantic

import spectre_server.core.events
import spectre_server.core.fields
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


def _validate_rx888mk2_hf(model) -> None:
    """Hardware constraints shared by every RX888MK2 HF mode."""
    validate_window_size(model.window_size)
    validate_output_type(model.output_type)

    if not model.antenna_port == spectre_server.core.flowgraphs.RX888MK2Port.HF:
        raise ValueError(
            f"Only the HF port is currently supported. Got {model.antenna_port}"
        )

    validate_in_range(
        model.center_frequency,
        lower_bound=HF_FREQ_LOWER_BOUND,
        upper_bound=HF_FREQ_UPPER_BOUND,
        name="center_frequency",
    )
    validate_in_range(
        model.rf_gain,
        lower_bound=RF_GAIN_LOWER_BOUND,
        upper_bound=RF_GAIN_UPPER_BOUND,
        name="rf_gain",
    )
    validate_in_range(
        model.if_gain,
        lower_bound=IF_GAIN_LOWER_BOUND,
        upper_bound=IF_GAIN_UPPER_BOUND,
        name="if_gain",
    )
    validate_one_of(model.sample_rate, HF_ALLOWED_SAMPLE_RATES, "sample_rate")
    validate_one_of(model.output_type, EXPECTED_OUTPUT_TYPES, "output_type")


class RX888MK2FixedCenterFrequency(
    spectre_server.core.flowgraphs.RX888MK2FixedCenterFrequencyModel,
    spectre_server.core.events.FixedCenterFrequencyModel,
):
    @pydantic.model_validator(mode="after")
    def validator(self, info: pydantic.ValidationInfo):
        if skip_validator(info):
            return self
        _validate_rx888mk2_hf(self)
        return self


class RX888MK2ECallisto(
    spectre_server.core.flowgraphs.RX888MK2FixedCenterFrequencyModel,
    spectre_server.core.events.ECallistoModel,
):
    # Override hardware defaults to e-CALLISTO operating values (FCF defaults to a coarser batch).
    sample_rate: spectre_server.core.fields.Field.sample_rate = 64e6
    batch_size: spectre_server.core.fields.Field.batch_size = 900

    @pydantic.model_validator(mode="after")
    def validator(self, info: pydantic.ValidationInfo):
        if skip_validator(info):
            return self
        _validate_rx888mk2_hf(self)

        validate_one_of(self.obs_lac, ["N", "S"], "obs_lac")
        validate_one_of(self.obs_loc, ["E", "W"], "obs_loc")
        validate_in_range(self.obs_lat, lower_bound=0, upper_bound=90, name="obs_lat")
        validate_in_range(self.obs_lon, lower_bound=0, upper_bound=180, name="obs_lon")

        for name in ("instrument", "object", "origin", "telescope"):
            if not getattr(self, name):
                raise ValueError(f"{name} must be a non-empty string.")
        return self
