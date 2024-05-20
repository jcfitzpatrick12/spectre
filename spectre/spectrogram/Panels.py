import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import matplotlib.dates as mdates
from matplotlib.colors import LogNorm
from matplotlib.axes import Axes
from datetime import datetime
from math import ceil


class Panels:
    def __init__(self, S, **kwargs):
        self.S = S

        self.panel_type_dict = {
                "integrated_power": self.integrated_power,
                "dBb": self.dBb,
                "raw": self.raw,
                "rawlog": self.rawlog,
                "time_slices": self.time_slices,
                "frequency_slices": self.frequency_slices,
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
        
        self.slice_at_times = kwargs.get("slice_at_times", None)
        if not self.slice_at_times is None:
            self.__check_requested_slice_at_times(self.slice_at_times)
        
        self.slice_at_frequencies = kwargs.get("slice_at_frequencies", None)
        if not self.slice_at_frequencies is None:
            self.__check_requested_slice_at_frequencies(self.slice_at_frequencies)


        self.fsize_head = kwargs.get("fsize_head", 20)        
        self.fsize = kwargs.get("fsize", 15)
        self.dB_vmin = kwargs.get("dB_vmin", -1)
        self.dB_vmax = kwargs.get("dB_vmax", 2)
        self.spectrogrwam_cmap = kwargs.get("spectrogram_cmap", 'gnuplot2')
        self.slice_cmap = kwargs.get("slice_cmap", cm.rainbow)
        self.slice_overlay_color = kwargs.get("slice_overlay_color", "lime")
        
        self.annotation_offset_step = kwargs.get("annotation_offset_step", 12)
        self.annotation_horizontal_offset = kwargs.get("annotation_horizontal_offset", 1.02)
        self.add_tag_to_annotation = kwargs.get("add_tag_to_annotation", False)

       
    def get_plot_method(self, panel_type: str):
        plot_method = self.panel_type_dict.get(panel_type, None)
        if plot_method is None:
            raise KeyError(f"{panel_type} is not valid. Expected one of {self.valid_panel_types}.")
        return plot_method
    

    def frequency_slices(self, ax: Axes, cax: Axes) -> None:
            # ensure that the slice_at_times keyword is non-empty
            if self.slice_at_times is None:
                raise ValueError(f"No times specified to slice spectrogram. Received {self.slice_at_times}.")

            ax.set_xlabel('Frequency [MHz]', size=self.fsize_head)
            ax.set_ylabel(f'DFT [{self.S.units}]', size=self.fsize_head)
            ax.tick_params(axis='x', labelsize=self.fsize)
            ax.tick_params(axis='y', labelsize=self.fsize)

            slices = []
            labels = []
            for time in self.slice_at_times:
                specific_time_of_slice, freq_MHz, slice = self.S.slice_at_time(at_time = time)
                # Adding annotation on the plot
                label_time = f"{round(specific_time_of_slice, 3)} [s]" if self.time_type == "time_seconds" else datetime.strftime(specific_time_of_slice, "%H:%M:%S.%f")
                if self.add_tag_to_annotation:
                    label_time = f"{label_time} "
                slices.append(slice)
                labels.append(label_time)

            self.__plot_slices(ax, cax, freq_MHz, slices, labels)
            return
    

    def time_slices(self, ax: Axes, cax: Axes) -> None:
            # ensure that the slice_at_times keyword is non-empty
            if self.slice_at_frequencies is None:
                raise ValueError(f"No times specified to slice spectrogram. Received {self.slice_at_times}.")

            ax.set_ylabel(f'DFT [{self.S.units}]', size=self.fsize_head)
            ax.tick_params(axis='x', labelsize=self.fsize)
            ax.tick_params(axis='y', labelsize=self.fsize)

            slices = []
            labels = []
            for frequency in self.slice_at_frequencies:
                times, specific_frequency_of_slice, slice = self.S.slice_at_frequency(at_frequency=frequency,
                                                                                      return_time_type = self.time_type)
                # Adding annotation on the plot
                label_frequency = f"{round(specific_frequency_of_slice, 3)} [MHz]" 
                slices.append(slice)
                labels.append(label_frequency)

            self.__plot_slices(ax, cax, times, slices, labels)
            return
    

    def integrated_power(self, ax: Axes, cax: Axes) -> None:
        times = self.times
        power = self.S.integrated_power()

        if self.time_type == "datetimes":
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.SecondLocator(interval=self.seconds_interval))

        ax.tick_params(axis='x', labelsize=self.fsize)
        ax.tick_params(axis='y', labelsize=self.fsize)
        ax.set_ylabel('Normalised Power', size=self.fsize_head)

        ax.step(times, power, where='mid')


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
        
        self.__overlay_slices(ax, cax)

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
        
        self.__overlay_slices(ax, cax)
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
        
        self.__overlay_slices(ax, cax)

    def __check_requested_slice_at_times(self, slice_at_times: list) -> None:
        # Check if the times provided match the expected type based on time_type attribute
        for time in slice_at_times:
            slice_type = type(time)

            if self.time_type == "time_seconds":
                if not (slice_type == float or slice_type == int):
                    raise TypeError(f"Unexpected type for slice_at_time, with Panels having time_type {self.time_type}. Received {type(time)}, expected float or int.")
                
            elif self.time_type == "datetimes":
                if not slice_type == datetime:
                    raise TypeError(f"Unexpected type for slice_at_time, with Panels having time_type {self.time_type}. Received {type(time)}, expected datetime.")
                
            else:
                raise ValueError(f"Must set a valid time type. Received {self.time_type}, expected one of {self.valid_time_types}.")
        return
    

    def __check_requested_slice_at_frequencies(self, slice_at_frequencies: list) -> None:
        # Check if the times provided match the expected type based on time_type attribute
        for slice in slice_at_frequencies:
            slice_type = type(slice)
            if not (slice_type == float or slice_type == int):
                raise TypeError(f"Unexpected type for frequency slice Received {slice_type}, expected either float or int.")
        return
    

    def __overlay_slices(self, ax: Axes, cax: Axes):
        if not self.slice_at_times is None:
            # color_iterator = iter(self.slice_color_base(np.linspace(0, 1, len(self.slice_at_times))))
            for slice in self.slice_at_times:
                # c = next(color_iterator)
                ax.axvline(x = slice, 
                           color = self.slice_overlay_color, 
                           linestyle='--')

        if not self.slice_at_frequencies is None:
                # color_iterator = iter(self.slice_color_base(np.linspace(0, 1, len(self.slice_at_frequencies))))
                for slice in self.slice_at_frequencies:
                    # c = next(color_iterator)
                    ax.axhline(y = slice, 
                               color = self.slice_overlay_color, 
                               linestyle='--')


    def __plot_slices(self, ax: Axes, cax: Axes, xvals: list, slices: list, labels: list):
            offset_step = self.annotation_offset_step # Vertical spacing between annotations
            color_iterator = iter(self.slice_cmap(np.linspace(0, 1, len(slices))))

            vertical_offset = 0  # Initial offset from the top
            for slice, label in zip(slices, labels):
                c = next(color_iterator)
                ax.step(xvals, slice, where='mid', color=c)
                ax.annotate(label, 
                            xy=(self.annotation_horizontal_offset, 0.98 - vertical_offset), 
                            xycoords='axes fraction',
                            color=c, 
                            verticalalignment='top', 
                            fontsize=self.fsize)
                
                # update the vertical offset
                vertical_offset += offset_step / ax.figure.dpi