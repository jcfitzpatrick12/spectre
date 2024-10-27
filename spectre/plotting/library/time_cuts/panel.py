# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional

from spectre.spectrograms.spectrogram import TimeCut
from spectre.spectrograms.spectrogram import Spectrogram
from spectre.plotting.base import BaseTimeSeriesPanel
from spectre.plotting.panel_register import register_panel

TIME_CUTS_PANEL_NAME = "time_cuts"

@register_panel(TIME_CUTS_PANEL_NAME)
class Panel(BaseTimeSeriesPanel):
    def __init__(self, 
                 spectrogram: Spectrogram, 
                 time_type: str = "seconds",
                 *frequencies: list[float],
                 dBb: bool = False,
                 peak_normalise: bool = False,
                 background_subtract: bool = False,
                 cmap: str = "Spectral",
                 **kwargs):
        super().__init__(spectrogram, time_type, **kwargs)
        self._frequencies = frequencies
        self._cmap = cmap
        self._dBb = dBb
        self._peak_normalise = peak_normalise
        self._background_subtract = background_subtract
        # map each cut frequency to the corresponding TimeCut dataclass
        self._time_cuts: Optional[dict[float, TimeCut]] = {} 
    

    @property
    def time_cuts(self) -> dict[float, TimeCut]:
        if not self._time_cuts:
            for frequency in self._frequencies:
                time_cut =  self._spectrogram.get_time_cut(frequency,
                                                           dBb = self._dBb,
                                                           peak_normalise = self._peak_normalise,
                                                           correct_background = self._background_subtract,
                                                           return_time_type=self._time_type)
                self._time_cuts[time_cut.frequency] = time_cut
        return self._time_cuts
    

    @property
    def frequencies(self) -> list[float]:
        return list(self.time_cuts.keys())


    def draw(self):
        for frequency, color in self.bind_to_colors():
            time_cut = self.time_cuts[frequency]
            self.ax.step(self.times, 
                         time_cut.cut, 
                         where='mid', 
                         color = color)
    

    def annotate_y_axis(self) -> None:
        if self._dBb:
            self.ax.set_ylabel('dBb')
        elif self._peak_normalise:
            return # no y-axis label
        else:
            self.ax.set_ylabel(f'{self._spectrogram.spectrum_type.capitalize()}')

    
    def bind_to_colors(self):
        return super().bind_to_colors(self.frequencies, cmap = self._cmap)