# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses


@dataclasses.dataclass(frozen=True)
class ReceiverName:
    """The name of a supported receiver.

    :ivar CUSTOM: A customisable receiver.
    :ivar SIGNAL_GENERATOR: A synthetic signal generator.
    :ivar RSP1A: SDRPlay RSP1A.
    :ivar RSP1B: SDRPlay RSP1B.
    :ivar RSPDUO: SDRPlay RSPduo.
    :ivar RSPDX: SDRPlay RSPdx.
    :ivar USRP: A general USRP receiver.
    :ivar B200MINI: USRP B200mini.
    :ivar HACKRF: Any general HackRF receiver.
    :ivar HACKRFONE: Hack RF One.
    :ivar RTLSDR: RTL-SDR.
    """

    CUSTOM = "custom"
    SIGNAL_GENERATOR = "signal_generator"
    RSP1A = "rsp1a"
    RSP1B = "rsp1b"
    RSPDUO = "rspduo"
    RSPDX = "rspdx"
    USRP = "usrp"
    B200MINI = "b200mini"
    HACKRF = "hackrf"
    HACKRFONE = "hackrfone"
    RTLSDR = "rtlsdr"
