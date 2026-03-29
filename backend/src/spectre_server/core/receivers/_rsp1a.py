# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses

import spectre_server.core.events
import spectre_server.core.flowgraphs
import spectre_server.core.models
import spectre_server.core.batches

from ._register import register_receiver
from ._base import Base
from ._names import ReceiverName


@dataclasses.dataclass(frozen=True)
class _Mode:
    FIXED_CENTER_FREQUENCY = "fixed_center_frequency"
    SWEPT_CENTER_FREQUENCY = "swept_center_frequency"


@register_receiver(ReceiverName.RSP1A)
class RSP1A(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_mode(
            _Mode.FIXED_CENTER_FREQUENCY,
            spectre_server.core.models.RSP1AFixedCenterFrequency,
            spectre_server.core.flowgraphs.RSP1AFixedCenterFrequency,
            spectre_server.core.events.FixedCenterFrequency,
            spectre_server.core.batches.IQStreamBatch,
        )

        self.add_mode(
            _Mode.SWEPT_CENTER_FREQUENCY,
            spectre_server.core.models.RSP1ASweptCenterFrequency,
            spectre_server.core.flowgraphs.RSP1ASweptCenterFrequency,
            spectre_server.core.events.SweptCenterFrequency,
            spectre_server.core.batches.IQStreamBatch,
        )
