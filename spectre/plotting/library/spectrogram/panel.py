# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from matplotlib.colors import LogNorm
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from warnings import warn

from spectre.plotting.base import BaseTimeSeriesPanel
from spectre.plotting.panel_register import register_panel

@register_panel("spectrogram")
class Panel(BaseTimeSeriesPanel):
    def __init__(self, 
                 *args, 
                 log_norm: bool = False,
                 dBb: bool = False,
                 vmin: float | None = -1,
                 vmax: float | None = 2,
                 cmap: str = "gnuplot2",
                 **kwargs):
        self._log_norm = log_norm
        self._dBb = dBb
        self._vmin = vmin
        self._vmax = vmax
        self._cmap = cmap
        super().__init__(*args, **kwargs)

    def draw(self, 
             fig: Figure, 
             ax: Axes):

        dynamic_spectra = self._spectrogram.dynamic_spectra_as_dBb if self._dBb else self._spectrogram.dynamic_spectra
        norm = LogNorm(vmin=np.nanmin(dynamic_spectra[dynamic_spectra > 0]), 
                       vmax=np.nanmax(dynamic_spectra)) if self._log_norm else None
        

        # Handle vmin/vmax and log_norm
        if self._log_norm and (self._vmin or self._vmax):
            warn("vmin/vmax will be ignored while using log_norm.")
            self._vmin = None 
            self._vmax = None
        
        # Plot the spectrogram with kwargs
        pcm = ax.pcolormesh(self.times, 
                            self._spectrogram.frequencies * 1e-6, 
                            dynamic_spectra,
                            vmin=self._vmin, 
                            vmax=self._vmax,
                            norm=norm, 
                            cmap=self._cmap)
        
        # Add colorbar if dBb is used
        if self._dBb:
            cbar = fig.colorbar(pcm, 
                                ax=ax, 
                                ticks=np.linspace(self._vmin, self._vmax, 6, dtype=int))
            cbar.set_label('dBb')

    def annotate_y_axis(self, 
                        ax: Axes):
        ax.set_ylabel('Frequency [MHz]')
        return