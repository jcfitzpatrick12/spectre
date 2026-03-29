# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from enum import Enum


class PanelName(Enum):
    """Literal corresponding to a fully implemented `BasePanel` subclass.

    :ivar SPECTROGRAM: Panel for visualising the full spectrogram.
    :ivar FREQUENCY_CUTS: Panel for visualising individual spectrums in a spectrogram.
    :ivar TIME_CUTS: Panel for visualising spectrogram data as time series of spectral components.
    :ivar INTEGRAL_OVER_FREQUENCY: Panel for visualising the spectrogram integrated over frequency.
    """

    SPECTROGRAM = "spectrogram"
    FREQUENCY_CUTS = "frequency_cuts"
    TIME_CUTS = "time_cuts"
    INTEGRAL_OVER_FREQUENCY = "integral_over_frequency"
