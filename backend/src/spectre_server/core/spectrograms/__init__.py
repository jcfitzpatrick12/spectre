# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""Create and transform spectrogram data."""

from ._spectrogram import Spectrogram, FrequencyCut, TimeCut, SpectrumUnit, TimeType
from ._transform import (
    frequency_chop,
    time_chop,
    frequency_average,
    time_average,
    join_spectrograms,
)

__all__ = [
    "Spectrogram",
    "FrequencyCut",
    "TimeCut",
    "SpectrumUnit",
    "frequency_chop",
    "time_chop",
    "frequency_average",
    "time_average",
    "join_spectrograms",
    "TimeType",
]
