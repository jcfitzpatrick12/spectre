# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""Real-time, extensible post-processing of SDR data into spectrograms."""

from ._base import Base
from ._fixed_center_frequency import FixedCenterFrequency, FixedCenterFrequencyModel
from ._swept_center_frequency import SweptCenterFrequency, SweptCenterFrequencyModel

from ._stfft import (
    stfft,
    get_buffer,
    get_window,
    get_fftw_obj,
    get_frequencies,
    get_times,
    get_cosine_signal,
    get_num_spectrums,
)

__all__ = [
    "Base",
    "FixedCenterFrequency",
    "FixedCenterFrequencyModel",
    "SweptCenterFrequency",
    "SweptCenterFrequencyModel",
    "stfft",
    "get_buffer",
    "get_window",
    "get_fftw_obj",
    "get_times",
    "get_frequencies",
    "get_num_spectrums",
    "get_cosine_signal",
]
