# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from matplotlib.colors import LogNorm
from warnings import warn

from spectre.plotting.base import BaseTimeSeriesPanel
from spectre.plotting.panel_register import register_panel

@register_panel("spectrogram")
class SpectrogramPanel(BaseTimeSeriesPanel):
    def __init__(self, 
                 *args, 
                 log_norm: bool = False,
                 dBb: bool = False,
                 vmin: float | None = -1,
                 vmax: float | None = 2,
                 cmap: str = "gnuplot2",
                 **kwargs):
        self.log_norm = log_norm
        self.dBb = dBb
        self.vmin = vmin
        self.vmax = vmax
        self.cmap = cmap
        super().__init__(*args, **kwargs)

    def draw(self, fig, ax):

        dynamic_spectra = self.spectrogram.dynamic_spectra_as_dBb if self.dBb else self.spectrogram.dynamic_spectra
        norm = LogNorm(vmin=np.nanmin(dynamic_spectra[dynamic_spectra > 0]), 
                       vmax=np.nanmax(dynamic_spectra)) if self.log_norm else None
        

        # Handle vmin/vmax and log_norm
        if self.log_norm and (self.vmin or self.vmax):
            warn("vmin/vmax will be ignored while using log_norm.")
            self.vmin = None 
            self.vmax = None
        
        # Plot the spectrogram with kwargs
        pcm = ax.pcolormesh(self.times, 
                            self.spectrogram.frequencies * 1e-6, 
                            dynamic_spectra,
                            vmin=self.vmin, 
                            vmax=self.vmax,
                            norm=norm, 
                            cmap=self.cmap)
        
        # Add colorbar if dBb is used
        if self.dBb:
            cbar = fig.colorbar(pcm, ax=ax, ticks=np.linspace(self.vmin, self.vmax, 6, dtype=int))
            cbar.set_label('dBb')

    def annotate_y_axis(self, ax):
        ax.set_ylabel('Frequency [MHz]')
        return