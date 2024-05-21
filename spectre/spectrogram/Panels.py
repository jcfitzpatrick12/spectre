import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import matplotlib.dates as mdates
from matplotlib.colors import LogNorm
from matplotlib.axes import Axes
from datetime import datetime
from math import ceil

from spectre.utils import array_helpers, datetime_helpers
from cfg import CONFIG

class Panels:
    def __init__(self, S, **kwargs):
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
        
        self.time_type = kwargs.get("time_type", "time_seconds")
        if self.time_type == "datetimes":
            self.times = S.datetimes
        elif self.time_type == "time_seconds":
            self.times = S.time_seconds
        else:
            raise ValueError(f"Must set a valid time type. Received {self.time_type}, expected one of {self.valid_time_types}.")
        
        self.slice_at_time = kwargs.get("slice_at_time", None)
        if not self.slice_at_time is None:
            self.check_requested_slice_at_time(self.slice_at_time)
        if self.time_type == "datetimes" and type(self.slice_at_time) == str:
            self.slice_at_time = datetime.strptime(self.slice_at_time, CONFIG.default_time_format)

        self.slice_at_frequency = kwargs.get("slice_at_frequency", None)
        if not self.slice_at_frequency is None:
            self.check_requested_slice_at_frequency(self.slice_at_frequency)

        self.background_interval = kwargs.get("background_interval", None)
        if not self.background_interval is None:
            self.check_background_interval(self.background_interval)
            self.set_background_indices()
        else:
            self.background_start_index = 0
            self.background_end_index = -1

        self.fsize_head = kwargs.get("fsize_head", 20)        
        self.fsize = kwargs.get("fsize", 15)

        self.dB_vmin = kwargs.get("dB_vmin", -1)
        self.dB_vmax = kwargs.get("dB_vmax", 2)
        self.spectrogram_cmap = kwargs.get("spectrogram_cmap", 'gnuplot2')

        self.slice_color = kwargs.get("slice_color", "dodgerblue")

        self.normalise_line_plots = kwargs.get("normalise_line_plots", False)

        self.annotation_horizontal_offset = kwargs.get("annotation_horizontal_offset", 1.02)
        self.annotation_vertical_offset = kwargs.get("annotation_vertical_offset", 0.96)
        self.add_tag_to_annotation = kwargs.get("add_tag_to_annotation", False)

       
    def get_plot_method(self, panel_type: str):
        plot_method = self.panel_type_dict.get(panel_type, None)
        if plot_method is None:
            raise KeyError(f"{panel_type} is not valid. Expected one of {self.valid_panel_types}.")
        return plot_method
    

    def frequency_slice(self, ax: Axes, cax: Axes) -> None:
            # ensure that the slice_at_times keyword is non-empty
            if self.slice_at_time is None:
                raise ValueError(f"No times specified to slice spectrogram. Received {self.slice_at_time}.")

            ax.set_xlabel('Frequency [MHz]', size=self.fsize_head)
            # ax.set_ylabel(f'DFT', size=self.fsize_head)
            ax.tick_params(axis='x', labelsize=self.fsize)
            ax.tick_params(axis='y', labelsize=self.fsize)

            specific_time_of_slice, freq_MHz, slice = self.S.slice_at_time(at_time = self.slice_at_time)

            if self.normalise_line_plots:
                slice -= np.nanmean(slice[self.background_start_index:self.background_end_index])
                slice /= np.nanmax(slice)

            # Adding annotation on the plot
            label_time = f"{round(specific_time_of_slice, 3)} [s]" if self.time_type == "time_seconds" else datetime.strftime(specific_time_of_slice, "%H:%M:%S.%f")
            if self.add_tag_to_annotation:
                label_time = f"tag:{self.S.tag} {label_time}"

            self.plot_slice(ax, cax, freq_MHz, slice, label_time)
            return
    

    def time_slice(self, ax: Axes, cax: Axes) -> None:
            # ensure that the slice_at_times keyword is non-empty
            if self.slice_at_frequency is None:
                raise ValueError(f"No times specified to slice spectrogram. Received {self.slice_at_time}.")

            # ax.set_ylabel(f'DFT', size=self.fsize_head)
            ax.tick_params(axis='x', labelsize=self.fsize)
            ax.tick_params(axis='y', labelsize=self.fsize)

            times, specific_frequency_of_slice, slice = self.S.slice_at_frequency(at_frequency=self.slice_at_frequency,
                                                                                    return_time_type = self.time_type)

            if self.normalise_line_plots:
                slice -= np.nanmean(slice[self.background_start_index:self.background_end_index])
                slice /= np.nanmax(slice)

            # Adding annotation on the plot
            label_frequency = f"{round(specific_frequency_of_slice, 3)} [MHz]" 
            if self.add_tag_to_annotation:
                label_frequency = f"tag:{self.S.tag} {label_frequency}"

            self.plot_slice(ax, cax, times, slice, label_frequency)
            return
    

    def integrate_over_frequency(self, ax: Axes, cax: Axes) -> None:
        times = self.times
        I = self.S.integrate_over_frequency()

        if self.normalise_line_plots:
            I -= np.nanmean(I[self.background_start_index:self.background_end_index])
            I /= np.nanmax(I)

        if self.time_type == "datetimes":
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.SecondLocator(interval=self.seconds_interval))

        ax.tick_params(axis='x', labelsize=self.fsize)
        ax.tick_params(axis='y', labelsize=self.fsize)

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
        cbar.set_label('dB above background', size=self.fsize_head)
        cbar.set_ticks(range(self.dB_vmin, self.dB_vmax+1, 1))
        # cbar.ax.tick_params(labelsize=self.fsize)

    
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

    def check_requested_slice_at_time(self, slice_at_time: float|int|datetime) -> None:
        slice_type = type(slice_at_time)
        if self.time_type == "time_seconds":
            if not (slice_type == float or slice_type == int):
                raise TypeError(f"Unexpected type for slice_at_time, with Panels having time_type {self.time_type}. Received {type(slice_at_time)}, expected float or int.")
            
        elif self.time_type == "datetimes":
            if not (slice_type == datetime or slice_type == str):
                raise TypeError(f"Unexpected type for slice_at_time, with Panels having time_type {self.time_type}. Received {type(slice_at_time)}, expected datetime or str.")
        else:
            raise ValueError(f"Must set a valid time type. Received {self.time_type}, expected one of {self.valid_time_types}.")
        return
    
    def check_background_interval(self, background_interval: list) -> None:
        background_start, background_end = background_interval[0], background_interval[1]
        self.check_requested_slice_at_time(background_start)
        self.check_requested_slice_at_time(background_end)

        if type(background_start) != type(background_end):
            raise ValueError(f"Background interval elements must be of equal type.")
        
        return
    
    def set_background_indices(self):
        if self.time_type == "time_seconds":                
            self.background_start_index = array_helpers.find_closest_index(self.background_interval[0], self.times,  enforce_strict_bounds=True)
            self.background_end_index = array_helpers.find_closest_index(self.background_interval[1], self.times, enforce_strict_bounds=True)
    
        elif self.time_type == "datetimes":
            if type(self.background_interval[0]) == str and type(self.background_interval[1]) == str:
                self.background_interval = [datetime.strptime(background_bound, CONFIG.default_time_format) for background_bound in self.background_interval]
            self.background_start_index = datetime_helpers.find_closest_index(self.background_interval[0], self.times, enforce_strict_bounds=True)
            self.background_end_index = datetime_helpers.find_closest_index(self.background_interval[1], self.times, enforce_strict_bounds=True)

        else:
            raise ValueError(f"Must set a valid time type. Received {self.time_type}, expected one of {self.valid_time_types}.")
        
        
    def check_requested_slice_at_frequency(self, slice_at_frequency: float|int) -> None:
        slice_type = type(slice_at_frequency)
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
            
