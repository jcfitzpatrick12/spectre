# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from typing import List, Optional, Tuple
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from spectre.spectrograms.spectrogram import Spectrogram
from spectre.plotting.base import BasePanel
from spectre.plotting.factory import get_panel
from spectre.plotting.library.time_cuts.panel import TIME_CUTS_PANEL_NAME
from spectre.plotting.library.frequency_cuts.panel import FREQUENCY_CUTS_PANEL_NAME
from spectre.plotting.library.spectrogram.panel import SPECTROGRAM_PANEL_NAME
from spectre.plotting.library.spectrogram.panel import Panel as SpectrogramPanel
from spectre.plotting.library.time_cuts.panel import Panel as TimeCutsPanel
from spectre.plotting.library.frequency_cuts.panel import Panel as FrequencyCutsPanel
from spectre.plotting import (
    SMALL_FONT_SIZE,
    MEDIUM_FONT_SIZE,
    LARGE_FONT_SIZE
)

class PanelStack: 
    def __init__(self, 
                 time_type: str,
                 figsize: Tuple[int, int] = (10, 10)):
        self._time_type = time_type
        self._figsize: Tuple[int, int] = figsize
        
        self._panels: List[BasePanel] = []
        self._fig: Figure = None
        self._axs: np.ndarray[Axes] = None


    @property
    def time_type(self) -> str:
        return self._time_type
    

    @property
    def panels(self) -> List[BasePanel]:
        return sorted(self._panels, key=lambda panel: panel.x_axis_type)
    

    @property
    def fig(self) -> Optional[Figure]:
        return self._fig
    

    @property
    def axs(self) -> Optional[np.ndarray[Axes]]:
        return np.atleast_1d(self._axs)
    

    @property
    def num_panels(self) -> int:
        return len(self._panels)


    def add_panel(self, 
                  panel_name: str, 
                  spectrogram: Spectrogram, 
                  *args,
                  **kwargs) -> None:
        panel = get_panel(panel_name, 
                          spectrogram, 
                          self._time_type, 
                          *args, 
                          **kwargs)
        self._panels.append(panel)


    def _init_font_sizes(self) -> None:
        plt.style.use('dark_background')
        plt.rc('font', size=SMALL_FONT_SIZE)          # controls default text sizes
        plt.rc('axes', titlesize=MEDIUM_FONT_SIZE)    # fontsize of the axes title
        plt.rc('axes', labelsize=MEDIUM_FONT_SIZE)    # fontsize of the x and y labels
        plt.rc('xtick', labelsize=SMALL_FONT_SIZE)    # fontsize of the tick labels
        plt.rc('ytick', labelsize=SMALL_FONT_SIZE)    # fontsize of the tick labels
        plt.rc('legend', fontsize=SMALL_FONT_SIZE)    # legend fontsize
        plt.rc('figure', titlesize=LARGE_FONT_SIZE)   # fontsize of the figure title


    def _init_figure(self) -> None:
        self._fig, self._axs = plt.subplots(self.num_panels, 
                                            1, 
                                            figsize=self._figsize, 
                                            layout="constrained")


    def _assign_axes_to_panels(self) -> None:
        shared_axes = {}
        for i, panel in enumerate(self.panels):
            panel.ax = self._axs[i] # set the panel ax
            panel.fig = self._fig
            if panel.x_axis_type not in shared_axes:
                shared_axes[panel.x_axis_type] = panel.ax
            else:
                panel.ax.sharex(shared_axes[panel.x_axis_type])


    def _overlay_time_cuts(self, 
                           time_cuts_panel: TimeCutsPanel) -> None:
        """Finds any corresponding spectrogram panels and overlays cuts onto the panel"""
        for panel in self.panels:
            is_corresponding_panel = (panel.name == SPECTROGRAM_PANEL_NAME) and (panel.tag == time_cuts_panel.tag)
            if is_corresponding_panel:
                spectrogram_panel: SpectrogramPanel = panel
                spectrogram_panel.overlay_time_cuts(time_cuts_panel)


    def _overlay_frequency_cuts(self, 
                                frequency_cuts_panel: FrequencyCutsPanel) -> None:
        """Finds any corresponding spectrogram panels and overlays cuts onto the panel"""
        for panel in self.panels:
            is_corresponding_panel = (panel.name == SPECTROGRAM_PANEL_NAME) and (panel.tag == frequency_cuts_panel.tag)
            if is_corresponding_panel:
                spectrogram_panel: SpectrogramPanel = panel
                spectrogram_panel.overlay_frequency_cuts(frequency_cuts_panel)
                
    

    def show(self) -> None:
        self._init_font_sizes()
        self._init_figure()
        self._assign_axes_to_panels()
        # find last panel through value overwrites per key (assumes self.panels is consistenly ordered)
        _last_panels = {panel.x_axis_type: panel for panel in self.panels}
        for panel in self.panels:
            panel.draw()
            panel.annotate_y_axis()
            if panel == _last_panels[panel.x_axis_type]:
                panel.annotate_x_axis()
            else:
                panel.hide_x_axis_labels()
                
            if panel.name == TIME_CUTS_PANEL_NAME:
                self._overlay_time_cuts(panel)
            
            if panel.name == FREQUENCY_CUTS_PANEL_NAME:
                self._overlay_frequency_cuts(panel)
            
        plt.show()
        return  