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
)
from ._soapy_validators import validate_output_type


class HackRFFixedCenterFrequency(
    spectre_server.core.flowgraphs.HackRFFixedCenterFrequencyModel,
    spectre_server.core.events.FixedCenterFrequencyModel,
):
    @pydantic.model_validator(mode="after")
    def validator(self, info: pydantic.ValidationInfo):
        if skip_validator(info):
            return self
        validate_nyquist_criterion(self.sample_rate, self.bandwidth)
        validate_window_size(self.window_size)
        validate_output_type(self.output_type)
        return self
