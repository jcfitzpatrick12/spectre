# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses


@dataclasses.dataclass(frozen=True)
class OutputType:
    """The type of samples produced by a source block."""

    FC32 = "fc32"
    FC64 = "fc64"
    SC8 = "sc8"
    SC16 = "sc16"


@dataclasses.dataclass(frozen=True)
class WindowType:
    HANN = "hann"
    BLACKMAN = "blackman"
    BOXCAR = "boxcar"
