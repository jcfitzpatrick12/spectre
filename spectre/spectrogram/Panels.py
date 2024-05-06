import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LogNorm
from matplotlib.axes import Axes
from math import ceil


class Panels:
    def __init__(self, S, **kwargs):
        self.S = S

        self.panel_type_dict = {
                "integrated_power": self.integrated_power,
                "dBb": self.dBb,
                "raw": self.raw,
                "rawlog": self.rawlog,
            }
        
        self.valid_panel_types = self.panel_type_dict.keys()
        self.seconds_interval = ceil(self.S.time_seconds[-1]/6)

        self.time_type = kwargs.get("time_type", "time_seconds")

        self.valid_time_types = ["datetimes", "time_seconds"]
        if self.time_type not in self.valid_time_types:
            raise ValueError(f"Must set a valid time type. Received {self.time_type}, expected one of {self.valid_time_types}.")

        self.fsize_head = kwargs.get("fsize_head", 20)        
        self.fsize = kwargs.get("fsize", 15)
        self.cmap = kwargs.get("cmap", 'gnuplot2')
        self.vmin = kwargs.get("vmin", -1)
        self.vmax = kwargs.get("vmax", 2)


       
    def get_plot_method(self, panel_type: str):
        plot_method = self.panel_type_dict.get(panel_type, None)
        if plot_method is None:
            raise KeyError(f"{panel_type} is not valid. Expected one of {self.valid_panel_types}.")
        return plot_method


    def integrated_power(self, ax: Axes, cax: Axes) -> None:

        if self.time_type == "datetimes":
            times = self.S.datetimes
        
        if self.time_type == "time_seconds":
            times = self.S.time_seconds

        power = self.S.integrated_power()

        ax.step(times, power, where='mid')

        if self.time_type == "datetimes":
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.SecondLocator(interval=self.seconds_interval))

        ax.tick_params(axis='x', labelsize=self.fsize)
        ax.tick_params(axis='y', labelsize=self.fsize)
        ax.set_ylabel('Normalised Power', size=self.fsize_head)


    def dBb(self, ax: Axes, cax: Axes) -> None:

        if self.time_type == "datetimes":
            times = self.S.datetimes
        
        if self.time_type == "time_seconds":
            times = self.S.time_seconds

        freq_MHz = self.S.freq_MHz

        if self.S.bvect is None:
            raise ValueError(f"Cannot plot in units of dBb, bvect is not specified. Got bvect={self.S.bvect}")

        dynamic_spectra = self.S.dynamic_spectra_as_dBb()

        pcolor_plot = ax.pcolormesh(times, 
                                    freq_MHz, 
                                    dynamic_spectra, 
                                    vmin=self.vmin, 
                                    vmax=self.vmax, 
                                    cmap=self.cmap)

        if self.time_type == "datetimes":
            # Format the x-axis to display time in HH:MM:SS
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.SecondLocator(interval=self.seconds_interval))

        # Assign the x and y labels with specified font size
        ax.set_ylabel('Frequency [MHz]', size=self.fsize_head)
        # Format the x and y tick labels with specified font size
        ax.tick_params(axis='x', labelsize=self.fsize)
        ax.tick_params(axis='y', labelsize=self.fsize)

        cax.axis("On")
        cbar = plt.colorbar(pcolor_plot,ax=ax,cax=cax)
        cbar.set_label('dB above background', size=self.fsize_head)
        cbar.set_ticks(range(self.vmin, self.vmax+1, 1))

    
    def rawlog(self, ax: Axes, cax: Axes) -> None:

        if self.time_type == "datetimes":
            times = self.S.datetimes
        
        if self.time_type == "time_seconds":
            times = self.S.time_seconds

        freq_MHz = self.S.freq_MHz
        dynamic_spectra = self.S.dynamic_spectra

        # Plot the spectrogram with LogNorm
        pcolor_plot = ax.pcolormesh(times, 
                                    freq_MHz, 
                                    dynamic_spectra, 
                                    norm=LogNorm(vmin=np.min(dynamic_spectra[dynamic_spectra > 0]), vmax=np.max(dynamic_spectra)),
                                    cmap=self.cmap)

        if self.time_type == "datetimes":
            # Format the x-axis to display time in HH:MM:SS
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.SecondLocator(interval=self.seconds_interval))

        # Assign the x and y labels with specified font size
        ax.set_ylabel('Frequency [MHz]', size=self.fsize_head)
        # Format the x and y tick labels with specified font size
        ax.tick_params(axis='x', labelsize=self.fsize)
        ax.tick_params(axis='y', labelsize=self.fsize)

        cax.axis("On")
        cbar = plt.colorbar(pcolor_plot,ax=ax,cax=cax)


    def raw(self, ax: Axes ,cax: Axes) -> None:

        if self.time_type == "datetimes":
            times = self.S.datetimes
        
        if self.time_type == "time_seconds":
            times = self.S.time_seconds

        freq_MHz = self.S.freq_MHz
        dynamic_spectra = self.S.dynamic_spectra
        pcolor_plot = ax.pcolormesh(times, 
                                    freq_MHz, 
                                    dynamic_spectra, 
                                    cmap=self.cmap)
        # Format the x-axis to display time in HH:MM:SS
        if self.time_type == "datetimes":
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.SecondLocator(interval=self.seconds_interval))

        # Assign the x and y labels with specified font size
        ax.set_ylabel('Frequency [MHz]', size=self.fsize_head)
        # Format the x and y tick labels with specified font size
        ax.tick_params(axis='x', labelsize=self.fsize)
        ax.tick_params(axis='y', labelsize=self.fsize)

