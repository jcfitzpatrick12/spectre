# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass

@dataclass
class DefaultFormats:
    small_size: int = 18
    medium_size: int = 21
    large_size: int = 24
    line_width: int = 3
    style: str = "dark_background"
    spectrogram_cmap: str = "gnuplot2"
    cuts_cmap: str = "winter"
    integral_over_frequency_color: str = "lime"


DEFAULT_FORMATS = DefaultFormats()