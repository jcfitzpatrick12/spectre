# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from matplotlib.figure import Figure
from matplotlib.axes import Axes

from spectre.plotting.base import BaseTimeSeriesPanel
from spectre.plotting.panel_register import register_panel

@register_panel("integral_over_frequency")
class Panel(BaseTimeSeriesPanel):
    def __init__(self, 
                 *args, 
                 peak_normalise: bool = False,
                 background_subtract: bool = False,
                 color: str = 'black',
                 **kwargs):
        self._peak_normalise = peak_normalise
        self._background_subtract = background_subtract
        self._color = color
        super().__init__(*args, **kwargs)


    def draw(self, 
             fig: Figure, 
             ax: Axes):
        I = self._spectrogram.integrate_over_frequency(correct_background = self._background_subtract,
                                                       peak_normalise = self._peak_normalise)
        ax.step(self.times, I, where="mid", color = self._color)
    

    def annotate_y_axis(self, 
                        ax: Axes):
        return