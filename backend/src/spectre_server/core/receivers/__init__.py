# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""A vendor-neutral interface for recording signals and spectrograms from SDRs."""

from ._register import register_receiver, get_registered_receivers
from ._factory import get_receiver, get_batch_cls
from ._config import (
    Config,
    read_config,
    write_config,
    get_config_file_path,
    parse_config_file_name,
)
from ._base import Base
from ._names import ReceiverName
from ._custom import Custom
from ._signal_generator import SignalGenerator
from ._rsp1a import RSP1A
from ._rsp1b import RSP1B
from ._rspduo import RSPduo
from ._rspdx import RSPdx
from ._usrp import USRP
from ._b200mini import B200mini
from ._hackrf import HackRF
from ._hackrfone import HackRFOne
from ._rtlsdr import RTLSDR
from ._record import record_signal, record_spectrograms

__all__ = [
    "register_receiver",
    "get_registered_receivers",
    "get_receiver",
    "get_batch_cls",
    "get_config_file_path",
    "parse_config_file_name",
    "ReceiverName",
    "Config",
    "read_config",
    "write_config",
    "Base",
    "Custom",
    "SignalGenerator",
    "RSP1A",
    "RSP1B",
    "RSPduo",
    "RSPdx",
    "USRP",
    "B200mini",
    "HackRF",
    "HackRFOne",
    "RTLSDR",
    "ReceiverName",
    "record_signal",
    "record_spectrograms",
]
