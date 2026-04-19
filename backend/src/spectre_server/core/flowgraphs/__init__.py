# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""Configurable, extensible GNURadio flowgraphs."""

from ._base import Base
from ._signal_generator import (
    SignalGeneratorCosineWave,
    SignalGeneratorCosineWaveModel,
    SignalGeneratorConstantStaircase,
    SignalGeneratorConstantStaircaseModel,
)
from ._rsp1a import (
    RSP1AFixedCenterFrequency,
    RSP1AFixedCenterFrequencyModel,
    RSP1ASweptCenterFrequency,
    RSP1ASweptCenterFrequencyModel,
)
from ._rsp1b import RSP1BFixedCenterFrequency, RSP1BFixedCenterFrequencyModel
from ._rspduo import (
    RSPduoFixedCenterFrequency,
    RSPduoFixedCenterFrequencyModel,
    RSPduoSweptCenterFrequency,
    RSPduoSweptCenterFrequencyModel,
    RSPduoPort,
)
from ._rspdx import (
    RSPdxFixedCenterFrequency,
    RSPdxFixedCenterFrequencyModel,
    RSPdxSweptCenterFrequency,
    RSPdxSweptCenterFrequencyModel,
    RSPdxPort,
)
from ._usrp import (
    USRPFixedCenterFrequency,
    USRPFixedCenterFrequencyModel,
    USRPSweptCenterFrequency,
    USRPSweptCenterFrequencyModel,
    USRPWireFormat,
)
from ._hackrf import HackRFFixedCenterFrequency, HackRFFixedCenterFrequencyModel
from ._rtlsdr import RTLSDRFixedCenterFrequency, RTLSDRFixedCenterFrequencyModel
from ._rx888mk2 import (
    RX888MK2FixedCenterFrequency,
    RX888MK2FixedCenterFrequencyModel,
    RX888MK2Port,
)

__all__ = [
    "Base",
    "SignalGeneratorCosineWave",
    "SignalGeneratorCosineWaveModel",
    "SignalGeneratorConstantStaircase",
    "SignalGeneratorConstantStaircaseModel",
    "RSP1AFixedCenterFrequency",
    "RSP1AFixedCenterFrequencyModel",
    "RSP1ASweptCenterFrequency",
    "RSP1ASweptCenterFrequencyModel",
    "RSP1BFixedCenterFrequency",
    "RSP1BFixedCenterFrequencyModel",
    "RSPduoFixedCenterFrequency",
    "RSPduoFixedCenterFrequencyModel",
    "RSPduoSweptCenterFrequency",
    "RSPduoSweptCenterFrequencyModel",
    "RSPduoPort",
    "RSPdxFixedCenterFrequency",
    "RSPdxFixedCenterFrequencyModel",
    "RSPdxSweptCenterFrequency",
    "RSPdxSweptCenterFrequencyModel",
    "RSPdxPort",
    "USRPFixedCenterFrequency",
    "USRPFixedCenterFrequencyModel",
    "USRPSweptCenterFrequency",
    "USRPSweptCenterFrequencyModel",
    "USRPWireFormat",
    "HackRFFixedCenterFrequency",
    "HackRFFixedCenterFrequencyModel",
    "RTLSDRFixedCenterFrequency",
    "RTLSDRFixedCenterFrequencyModel",
    "RX888MK2FixedCenterFrequency",
    "RX888MK2FixedCenterFrequencyModel",
    "RX888MK2Port",
]
