# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses


@dataclasses.dataclass
class PanelFormat:
    """Specifies formatting options for a panel, including font sizes, line styles,
    colour maps, and general visual settings.

    These formatting values can be applied consistently across all panels within a `PanelStack`,
    but are optional.

    :ivar small_size: Font size for small text elements, defaults to 18.
    :ivar medium_size: Font size for medium text elements, defaults to 21.
    :ivar large_size: Font size for large text elements, defaults to 24.
    :ivar line_width: Thickness of lines in the plot, defaults to 3.
    :ivar line_color: Colour used for line elements, defaults to "lime".
    :ivar line_cmap: Colormap applied to line-based visual elements, defaults to "winter".
    :ivar style: Matplotlib style applied to the panel, defaults to "dark_background".
    :ivar spectrogram_cmap: Colormap applied to spectrogram plots, defaults to "gnuplot2".
    """

    small_size: int = 18
    medium_size: int = 21
    large_size: int = 24
    line_width: int = 3
    line_color: str = "lime"
    line_cmap: str = "winter"
    style: str = "dark_background"
    spectrogram_cmap: str = "gnuplot2"
