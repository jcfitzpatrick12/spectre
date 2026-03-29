# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import pydantic

import spectre_server.core.fields
import spectre_server.core.events
import spectre_server.core.flowgraphs

from ._validators import skip_validator, validate_window_size


class SignalGeneratorCosineWaveModel(
    spectre_server.core.flowgraphs.SignalGeneratorCosineWaveModel,
    spectre_server.core.events.FixedCenterFrequencyModel,
):
    window_type: spectre_server.core.fields.Field.window_type = (
        spectre_server.core.fields.WindowType.BOXCAR
    )

    @pydantic.model_validator(mode="after")
    def validator(self, info: pydantic.ValidationInfo):
        if skip_validator(info):
            return self
        validate_window_size(self.window_size)

        if not self.window_type == spectre_server.core.fields.WindowType.BOXCAR:
            raise ValueError(
                f"The window type must be boxcar. Got '{self.window_type}'"
            )
        if self.sample_rate % self.frequency != 0:
            raise ValueError(
                "The sampling rate must be some integer multiple of frequency"
            )

        a = self.sample_rate / self.frequency
        if a < 2:
            raise ValueError(
                (
                    f"The ratio of sampling rate over frequency must be greater than two. "
                    f"Got {a}"
                )
            )
        p = self.window_size / a
        if self.window_size % a != 0:
            raise ValueError(
                f"The number of sampled cycles must be a positive natural number. Computed p={p}."
            )

        return self


class SignalGeneratorConstantStaircaseModel(
    spectre_server.core.flowgraphs.SignalGeneratorConstantStaircaseModel,
    spectre_server.core.events.FixedCenterFrequencyModel,
):
    window_type: spectre_server.core.fields.Field.window_type = (
        spectre_server.core.fields.WindowType.BOXCAR
    )

    @pydantic.model_validator(mode="after")
    def validator(self, info: pydantic.ValidationInfo):
        if skip_validator(info):
            return self
        validate_window_size(self.window_size)
        if not self.window_type == spectre_server.core.fields.WindowType.BOXCAR:
            raise ValueError(
                f"The window type must be boxcar. Got '{self.window_type}'"
            )
        if self.frequency_hop != self.sample_rate:
            raise ValueError(f"The frequency hop must be equal to the sampling rate")

        if self.min_samples_per_step > self.max_samples_per_step:
            raise ValueError(
                (
                    f"Minimum samples per step cannot be greater than the maximum samples per step. "
                    f"Got {self.min_samples_per_step}, which is greater than {self.max_samples_per_step}"
                )
            )
        return self
