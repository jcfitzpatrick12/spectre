# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from typing import List, Optional, Tuple
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from spectre.spectrograms.spectrogram import Spectrogram
from spectre.plotting.factory import get_panel
from spectre.plotting.base import BasePanel

class PanelStack: 
    def __init__(self, 
                 time_type: str,
                 figsize: Tuple[int, int] = (10, 10)):
        self._time_type = time_type
        self._panels: List[BasePanel] = [] # no panels yet
        self._figsize: Tuple[int, int] = figsize
        self._fig: Figure = None
        self._axs: np.ndarray[Axes] = None


    @property
    def time_type(self) -> str:
        return self._time_type
    

    @property
    def panels(self) -> List[BasePanel]:
        return sorted(self._panels, key=lambda panel: panel.x_axis_type)
    

    @property
    def grouped_panels(self) -> dict[str, list[BasePanel]]:
        _grouped_panels: dict[str, list[BasePanel]] = {}
        for i, panel in enumerate(self.panels):
            panel.index = i  # set the panel index
            if panel.x_axis_type not in _grouped_panels:
                _grouped_panels[panel.x_axis_type] = [panel]
            else:
                _grouped_panels[panel.x_axis_type].append(panel)
        return _grouped_panels
    

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
                  **kwargs) -> None:
        panel = get_panel(panel_name, spectrogram, self._time_type, **kwargs)
        self._panels.append(panel)


    def _init_figure(self) -> None:
        self._fig, self._axs = plt.subplots(self.num_panels, 
                                            1, 
                                            figsize=self._figsize, 
                                            layout="constrained")

        # Share x-axis within each group
        for panel_group in self.grouped_panels.values():
            if len(panel_group) > 1:
                last_panel = panel_group[-1]
                for panel in panel_group:
                    self.axs[panel.index].sharex = self.axs[last_panel.index]


    def show(self) -> None:
        self._init_figure()
        for panel in self.panels:
            ax = self.axs[panel.index]
            panel.draw(self._fig, ax)
            panel.annotate_y_axis(ax) 
            # Annotate only the last panel in each group with the x-axis labels
            is_last_in_group = any(panel == group[-1] for group in self.grouped_panels.values())
            if is_last_in_group:
                panel.annotate_x_axis(ax)
            else:
                panel.hide_x_axis_numbers(ax)

        plt.show()


    
#     # def _draw_time_slices(self, fig, ax, **kwargs):
#     #     for frequency, color in self._bind_frequencies_to_colors():
#     #         frequency_of_slice, _, time_slice = self.spectrogram.slice_at_frequency(
#     #             frequency, dBb=kwargs.get('dBb', False), peak_normalise=kwargs.get('normalise_line_plots', False))
#     #         ax.step(self.times, time_slice, where='mid', color=color)

#     #     if kwargs.get('dBb', False):
#     #         ax.set_ylabel('dBb')
    
#     # def _overlay_time_slices(self, fig, ax, **kwargs):
#     #     for frequency, color in self._bind_frequencies_to_colors():
#     #         ax.axhline(frequency * 1e-6, color=color)
    
#     # def _annotate_time_axis(self, fig, ax, **kwargs):
#     #     if self.time_type == "seconds":
#     #         ax.set_xlabel('Time [s]', size=15)
#     #     else:
#     #         ax.set_xlabel('Time [UTC]', size=15)
#     #         ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))