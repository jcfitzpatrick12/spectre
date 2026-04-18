# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import pydantic

import spectre_server.core.events
import spectre_server.core.flowgraphs

from ._validators import (
    skip_validator,
    validate_window_size,
)
from ._soapy_validators import validate_output_type


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
        return self
