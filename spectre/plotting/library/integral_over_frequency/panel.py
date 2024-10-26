# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from matplotlib.figure import Figure
from matplotlib.axes import Axes

from spectre.plotting.base import BaseTimeSeriesPanel
from spectre.plotting.panel_register import register_panel

INTEGRAL_OVER_FREQUENCY_PANEL_NAME = "integral_over_frequency"

@register_panel(INTEGRAL_OVER_FREQUENCY_PANEL_NAME)
class Panel(BaseTimeSeriesPanel):
    def __init__(self, 
                 *args, 
                 peak_normalise: bool = False,
                 background_subtract: bool = False,
                 color: str = 'lime',
                 **kwargs):
        super().__init__(*args, **kwargs)
        self._peak_normalise = peak_normalise
        self._background_subtract = background_subtract
        self._color = color


    def draw(self):
        I = self._spectrogram.integrate_over_frequency(correct_background = self._background_subtract,
                                                       peak_normalise = self._peak_normalise)
        self.ax.step(self.times, I, where="mid", color = self._color)
 

    def annotate_y_axis(self):
        return  


    def _set_name(self) -> None:
        self._name = INTEGRAL_OVER_FREQUENCY_PANEL_NAME
    
