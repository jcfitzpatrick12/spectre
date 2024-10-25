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




        

# Plots may look like
# <plot> <colorbar>
# <plot>
# <plot>
# <plot> <color bar>

# PanelStack (a class which stacks panels, defined by the user)
#   -> init plot
#   -> method to add panel (doesn't populate yet, adds to internal attributes)
#   -> method to plot! Takes internally stored attributes 

# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# from matplotlib.colors import LogNorm
# from matplotlib.pyplot import cm
# from matplotlib.figure import Figure
# from matplotlib.gridspec import GridSpec
# from matplotlib.axes import Axes

# class Panel:
#     def __init__(self, spectrogram: Spectrogram, panel_type: str):
#         return
    
#     def 

# class PanelManager:
#     def __init__(self):
#         self.fig = None
#         self.gs = None
#         self.panel_count = 0

#     def init_figure(self):
#         self.fig: Figure = plt.figure(figsize=(8, 6))
#         self.gs: GridSpec = GridSpec(1, 1)  # Start with one row (1x1 grid)
#         self._panel_count: int = 0
#         self._panel_map = {} 

#     def add_panel(self, 
#                   spectrogram: Spectrogram, 
#                   panel_type: str):
#         self._panel_count += 1
#         self._panel_map[self.panel_count] = panel_type

#         # Adjust the GridSpec to accommodate the new panel
#         self.gs = GridSpec(self.panel_count, 1)

#         # Create empty Axes for each panel added so far
#         for i in range(self.panel_count):
#             ax = self.fig.add_subplot(self.gs[i, 0])
#             ax.set_title(f"Panel {i + 1}")


#     def show(self):
#         """Displays the figure with all added panels."""
#         plt.tight_layout()
#         plt.show()


# class TimeSeries:
#     def __init__(self, spectrogram: Spectrogram):
#         self.spectrogram = spectrogram

#     def plot(self, 
#              time_type: str = "seconds",
#              dBb: bool = False,
#              log_norm: bool = False,
#              integrate_over_frequency: bool = False,
#              slice_at_frequencies: List[float] | None = None,
#              **kwargs):
        
#         num_panels = 1 + (integrate_over_frequency) + (slice_at_frequencies is not None)
#         # Create the figure and axes
#         fig, axs = self._init_plot(num_panels)
        
#     #     # Draw the spectrogram
#     #     self._draw_spectrogram(fig, axs[0], **plot_options)
        
#     #     # Handle additional panels
#     #     if self.plot_options.get('integrate_over_frequency', False):
#     #         self._draw_integral_over_frequency(fig, axs[1], **plot_options)
#     #     if self.plot_options.get('slice_at_frequencies'):
#     #         self._draw_time_slices(fig, axs[-1], **plot_options)
#     #         self._overlay_time_slices(fig, axs[0], **plot_options)
        
#     #     self._annotate_time_axis(fig, axs[-1], **plot_options)
#     #     plt.show()

#     def _init_plot(self, num_panels: int):
#         small_size, medium_size, large_size = 12, 15, 18
#         plt.rc('font', size=small_size)
#         plt.rc('axes', titlesize=small_size)
#         plt.rc('xtick', labelsize=small_size)
#         plt.rc('ytick', labelsize=small_size)
#         plt.rc('legend', fontsize=small_size)
#         plt.rc('figure', titlesize=large_size)
        
#         # Set up figure and axes
#         return plt.subplots(num_panels, 
#                             1, 
#                             sharex=True, 
#                             layout='constrained')

#     # def _draw_spectrogram(self, fig, ax, **kwargs):
#     #     # Merge the method-specific kwargs with class-level plot options
#     #     plot_options = {**self.plot_options, **kwargs}
        
#     #     dynamic_spectra = self.spectrogram.dynamic_spectra_as_dBb if plot_options.get('dBb', False) else self.spectrogram.dynamic_spectra
#     #     norm = LogNorm(vmin=np.nanmin(dynamic_spectra[dynamic_spectra > 0]), vmax=np.nanmax(dynamic_spectra)) if plot_options.get('log_norm', False) else None
        
#     #     # Handle vmin/vmax and log_norm
#     #     if plot_options.get('log_norm') and (plot_options.get('vmin') or plot_options.get('vmax')):
#     #         warn("vmin/vmax will be ignored when using log_norm.")
        
#     #     # Plot the spectrogram with kwargs
#     #     pcm = ax.pcolormesh(self.times, self.spectrogram.frequencies * 1e-6, dynamic_spectra,
#     #                         vmin=plot_options.get('vmin'), vmax=plot_options.get('vmax'),
#     #                         norm=norm, cmap=plot_options.get('cmap'), shading=plot_options.get('shading'))
        
#     #     # Add colorbar if dBb is used
#     #     if plot_options.get('dBb'):
#     #         cbar = fig.colorbar(pcm, ax=ax, ticks=np.linspace(plot_options.get('vmin'), plot_options.get('vmax'), NUM_CBAR_TICKS, dtype=int))
#     #         cbar.set_label('dBb')
        
#     #     ax.set_ylabel('Frequency [MHz]')
    
#     # def _draw_integral_over_frequency(self, fig, ax, **kwargs):
#     #     line_options = {**DEFAULT_LINE_OPTIONS, **kwargs}
        
#     #     I = self.spectrogram.integrate_over_frequency(peak_normalise=kwargs.get('normalise_line_plots', False))
        
#     #     ax.step(self.times, I, where='mid', **line_options)
#     #     if not kwargs.get('normalise_line_plots', False):
#     #         ax.set_ylabel(f'{self.spectrogram.spectrum_type}')
    
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