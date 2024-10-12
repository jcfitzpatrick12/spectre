# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import matplotlib.dates as mdates
from matplotlib.colors import LogNorm
from matplotlib.axes import Axes
from datetime import datetime
from math import ceil


class Panels:
    def __init__(self, 
                 S,
                 time_type="time_seconds",
                 slice_at_time=None,
                 slice_at_frequency=None,
                 background_interval=None,
                 normalise_line_plots=False,
                 fsize_head=17,
                 fsize=15,
                 dB_vmin=-1,
                 dB_vmax=5,
                 spectrogram_cmap="gnuplot2",
                 slice_color="dodgerblue",
                 slice_type="raw",
                 annotation_horizontal_offset=1.02,
                 annotation_vertical_offset=0.96,
                 ):
        
        self.S = S

        self.panel_type_dict = {
                "integrate_over_frequency": self.integrate_over_frequency,
                "dBb": self.dBb,
                "raw": self.raw,
                "rawlog": self.rawlog,
                "time_slice": self.time_slice,
                "frequency_slice": self.frequency_slice,
            }

        self.valid_panel_types = self.panel_type_dict.keys()

        self.seconds_interval = ceil((self.S.time_seconds[-1] - self.S.time_seconds[0])/6)
        
        self.time_type=time_type
        if self.time_type == "datetimes":
            self.times = S.datetimes
        elif self.time_type == "time_seconds":
            self.times = S.time_seconds
        else:
            raise ValueError(f"Must set a valid time type. Received {self.time_type}, expected one of {self.valid_time_types}.")
        
        self.slice_at_time = slice_at_time
        if not self.slice_at_time is None:
            self.check_slice_at_time()
        if self.time_type == "datetimes" and type(self.slice_at_time) == str:
            self.slice_at_time = datetime.strptime(self.slice_at_time, DEFAULT_TIME_FORMAT)
        
        self.slice_at_frequency = slice_at_frequency
        if not self.slice_at_frequency is None:
            self.check_slice_at_frequency()

        self.background_interval = background_interval
        if not self.background_interval is None:
            self.S.set_background(self.background_interval)
        
        self.normalise_line_plots = normalise_line_plots

        self.slice_color = slice_color
        self.slice_type = slice_type
        if slice_type == "dBb":
            self.S.slice_type = "dBb"
        elif slice_type == "raw":
            self.S.slice_type = "raw"
        else:
            raise ValueError("Slice type is not recognised. Expected \"raw\" or \"dBb\".")
        
        self.fsize_head = fsize_head
        self.fsize = fsize
        self.dB_vmin = dB_vmin
        self.dB_vmax = dB_vmax
        self.spectrogram_cmap = spectrogram_cmap
        self.annotation_horizontal_offset = annotation_horizontal_offset
        self.annotation_vertical_offset= annotation_vertical_offset
       
    def get_plot_method(self, panel_type: str):
        plot_method = self.panel_type_dict.get(panel_type, None)
        if plot_method is None:
            raise KeyError(f"{panel_type} is not valid. Expected one of {self.valid_panel_types}.")
        return plot_method
    

    def frequency_slice(self, ax: Axes, cax: Axes) -> None:
            # ensure that the slice_at_times keyword is non-empty
            if self.slice_at_time is None:
                raise ValueError(f"No times specified to slice spectrogram. Received {self.slice_at_time}.")

            if self.normalise_line_plots:
                normalise_frequency_slice = True
            else:
                normalise_frequency_slice = False

            specific_time_of_slice, freq_MHz, slice = self.S.slice_at_time(at_time = self.slice_at_time,
                                                                           normalise_frequency_slice = normalise_frequency_slice,
                                                                           slice_type = self.slice_type)


            if self.S.slice_type == "dBb":
                ax.set_ylabel(f"{self.S.slice_type}", size=self.fsize_head)
            elif (self.S.slice_type == "raw") and not self.normalise_line_plots:
                ax.set_ylabel(f'{self.S.units}', size=self.fsize_head)
            else:
                pass

            ax.set_xlabel('Frequency [MHz]', size=self.fsize_head)
            ax.tick_params(axis='x', labelsize=self.fsize)
            ax.tick_params(axis='y', labelsize=self.fsize)

            label = f"tag:{self.S.tag}"

            self.plot_slice(ax, cax, freq_MHz, slice, label)
            return
    

    def time_slice(self, ax: Axes, cax: Axes) -> None:
            # ensure that the slice_at_times keyword is non-empty
            if self.slice_at_frequency is None:
                raise ValueError(f"No frequencies specified to slice spectrogram. Received {self.slice_at_time}.")

            if self.normalise_line_plots:
                normalise_time_slice = True
                background_subtract = True
            else:
                normalise_time_slice = False
                background_subtract = False

            times, specific_frequency_of_slice, slice = self.S.slice_at_frequency(at_frequency=self.slice_at_frequency,
                                                                                    return_time_type = self.time_type,
                                                                                    normalise_time_slice = normalise_time_slice,
                                                                                    slice_type = self.slice_type,
                                                                                    background_subtract = background_subtract)
            
            if self.S.slice_type == "dBb":
                ax.set_ylabel(f"{self.S.slice_type}", size=self.fsize_head)
            elif (self.S.slice_type == "raw") and not self.normalise_line_plots:
                ax.set_ylabel(f'{self.S.units}', size=self.fsize_head)
            else:
                pass

            ax.tick_params(axis='x', labelsize=self.fsize)
            ax.tick_params(axis='y', labelsize=self.fsize)
            label = f"tag:{self.S.tag}"

            self.plot_slice(ax, cax, times, slice, label)
            return
    

    def integrate_over_frequency(self, ax: Axes, cax: Axes) -> None:
        times = self.times

        if self.normalise_line_plots:
            normalise_integral_over_frequency = True
            background_subtract = True
        else:
            normalise_integral_over_frequency = False
            background_subtract = False
        
        I = self.S.integrate_over_frequency(normalise_integral_over_frequency = normalise_integral_over_frequency,
                                            background_subtract = background_subtract)


        if self.time_type == "datetimes":
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.SecondLocator(interval=self.seconds_interval))

        ax.tick_params(axis='x', labelsize=self.fsize)
        ax.tick_params(axis='y', labelsize=self.fsize)

        if not self.normalise_line_plots:
            ax.set_ylabel(f'{self.S.units}', size=self.fsize_head)

        label = f"tag:{self.S.tag}"
        ax.annotate(label, 
            xy=(self.annotation_horizontal_offset, self.annotation_vertical_offset), 
            xycoords='axes fraction',
            color=self.slice_color, 
            verticalalignment='top', 
            fontsize=self.fsize)

        ax.step(times, I, where='mid', color=self.slice_color)


    def dBb(self, ax: Axes, cax: Axes) -> None:

        times = self.times
        freq_MHz = self.S.freq_MHz

        if self.S.bvect is None:
            raise ValueError(f"Cannot plot in units of dBb, bvect is not specified. Got bvect={self.S.bvect}")

        dynamic_spectra = self.S.dynamic_spectra_as_dBb()

        if self.time_type == "datetimes":
            # Format the x-axis to display time in HH:MM:SS
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.SecondLocator(interval=self.seconds_interval))

        # Assign the x and y labels with specified font size
        ax.set_ylabel('Frequency [MHz]', size=self.fsize_head)
        # Format the x and y tick labels with specified font size
        ax.tick_params(axis='x', labelsize=self.fsize)
        ax.tick_params(axis='y', labelsize=self.fsize)

        pcolor_plot = ax.pcolormesh(times, 
                            freq_MHz, 
                            dynamic_spectra, 
                            vmin=self.dB_vmin, 
                            vmax=self.dB_vmax, 
                            cmap=self.spectrogram_cmap)
        
        self.overlay_slices(ax, cax)

        cax.axis("On")
        cbar = plt.colorbar(pcolor_plot,ax=ax,cax=cax)
        cbar.set_label('dBb', size=self.fsize_head)
        tick_step = ceil((self.dB_vmax-self.dB_vmin)/6)
        cbar.set_ticks(range(self.dB_vmin, self.dB_vmax+1, tick_step))
        cbar.ax.tick_params(labelsize=self.fsize)

    
    def rawlog(self, ax: Axes, cax: Axes) -> None:

        times = self.times
        freq_MHz = self.S.freq_MHz
        dynamic_spectra = self.S.dynamic_spectra


        if self.time_type == "datetimes":
            # Format the x-axis to display time in HH:MM:SS
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.SecondLocator(interval=self.seconds_interval))

        # Assign the x and y labels with specified font size
        ax.set_ylabel('Frequency [MHz]', size=self.fsize_head)
        # Format the x and y tick labels with specified font size
        ax.tick_params(axis='x', labelsize=self.fsize)
        ax.tick_params(axis='y', labelsize=self.fsize)

        # Plot the spectrogram with LogNorm
        pcolor_plot = ax.pcolormesh(times, 
                                    freq_MHz, 
                                    dynamic_spectra, 
                                    norm=LogNorm(vmin=np.min(dynamic_spectra[dynamic_spectra > 0]), vmax=np.max(dynamic_spectra)),
                                    cmap=self.spectrogram_cmap)
        
        self.overlay_slices(ax, cax)
        cax.axis("On")
        cbar = plt.colorbar(pcolor_plot, ax=ax, cax=cax)
        # cbar.ax.tick_params(labelsize=self.fsize)


    def raw(self, ax: Axes ,cax: Axes) -> None:
        times = self.times
        freq_MHz = self.S.freq_MHz
        dynamic_spectra = self.S.dynamic_spectra

        # Format the x-axis to display time in HH:MM:SS
        if self.time_type == "datetimes":
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.SecondLocator(interval=self.seconds_interval))

        # Assign the x and y labels with specified font size
        ax.set_ylabel('Frequency [MHz]', size=self.fsize_head)
        # Format the x and y tick labels with specified font size
        ax.tick_params(axis='x', labelsize=self.fsize)
        ax.tick_params(axis='y', labelsize=self.fsize)

        pcolor_plot = ax.pcolormesh(times, 
                                    freq_MHz, 
                                    dynamic_spectra, 
                                    cmap=self.spectrogram_cmap)
        
        self.overlay_slices(ax, cax)

    def check_slice_at_time(self) -> None:
        slice_type = type(self.slice_at_time)
        if self.time_type == "time_seconds":
            if not (slice_type == float or slice_type == int):
                raise TypeError(f"Unexpected type for slice_at_time, with Panels having time_type {self.time_type}. Received {slice_type}, expected float or int.")
            
        elif self.time_type == "datetimes":
            if not (slice_type == datetime or slice_type == str):
                raise TypeError(f"Unexpected type for slice_at_time, with Panels having time_type {self.time_type}. Received {slice_type}, expected datetime or str.")
        else:
            raise ValueError(f"Must set a valid time type. Received {self.time_type}, expected one of {self.valid_time_types}.")
        return
    
        
    def check_slice_at_frequency(self) -> None:
        slice_type = type(self.slice_at_frequency)
        if not (slice_type == float or slice_type == int):
            raise TypeError(f"Unexpected type for frequency slice Received {slice_type}, expected either float or int.")
        return
    

    def overlay_slices(self, ax: Axes, cax: Axes):
        if not self.slice_at_time is None:
            ax.axvline(x = self.slice_at_time, 
                        color = self.slice_color, 
                        linestyle='--')

        if not self.slice_at_frequency is None:
            ax.axhline(y = self.slice_at_frequency, 
                        color = self.slice_color, 
                        linestyle='--')


    def plot_slice(self, ax: Axes, cax: Axes, xvals: list, slice: list, label: list):
            ax.tick_params(axis='y', labelsize=self.fsize)
            ax.step(xvals, slice, where='mid', color=self.slice_color)
            ax.annotate(label, 
                        xy=(self.annotation_horizontal_offset, self.annotation_vertical_offset), 
                        xycoords='axes fraction',
                        color=self.slice_color, 
                        verticalalignment='top', 
                        fontsize=self.fsize)
            
