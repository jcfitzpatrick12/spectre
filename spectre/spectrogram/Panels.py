import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LogNorm
from matplotlib.axes import Axes
from math import ceil


class Panels:
    def __init__(self, S):
        self.S = S

        self.panel_type_dict = {
                "integrated_power": self.integrated_power,
                "dBb": self.dBb,
                "raw": self.raw,
                "rawlog": self.rawlog,
            }
        
        self.valid_panel_types = self.panel_type_dict.keys()
        
        self.fsize_head=20
        self.fsize=15
        self.cmap = 'gnuplot2'

        self.seconds_interval = ceil(self.S.time_seconds[-1]/3)

       
    def get_plot_method(self, panel_type: str):
        plot_method = self.panel_type_dict.get(panel_type, None)
        if plot_method is None:
            raise KeyError(f"{panel_type} is not valid. Expected one of {self.valid_panel_types}.")
        return plot_method


    def integrated_power(self, ax: Axes, cax: Axes) -> None:
        datetimes = self.S.datetimes
        power = self.S.integrated_power()

        ax.step(datetimes, power, where='mid')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.SecondLocator(interval=self.seconds_interval))
        ax.tick_params(axis='x', labelsize=self.fsize)
        ax.tick_params(axis='y', labelsize=self.fsize)
        ax.set_ylabel('Normalised Power', size=self.fsize_head)


    def dBb(self, ax: Axes, cax: Axes) -> None:
        datetimes = self.S.datetimes
        freq_MHz = self.S.freq_MHz

        if self.S.bvect is None:
            raise ValueError(f"Cannot plot in units of dBb, bvect is not specified. Got bvect={self.S.bvect}")

        dynamic_spectra = self.S.dynamic_spectra_as_dBb()

        vmin = -1
        vmax = 5

        pcolor_plot = ax.pcolormesh(datetimes, 
                                    freq_MHz, 
                                    dynamic_spectra, 
                                    vmin=vmin, 
                                    vmax=vmax, 
                                    cmap=self.cmap)
        
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
        cbar.set_ticks(range(vmin, vmax+1, 1))

    
    def rawlog(self, ax: Axes, cax: Axes) -> None:
        freq_MHz = self.S.freq_MHz
        datetimes = self.S.datetimes
        dynamic_spectra = self.S.dynamic_spectra

        # Plot the spectrogram with LogNorm
        pcolor_plot = ax.pcolormesh(datetimes, 
                                    freq_MHz, 
                                    dynamic_spectra, 
                                    norm=LogNorm(vmin=np.min(dynamic_spectra[dynamic_spectra > 0]), vmax=np.max(dynamic_spectra)),
                                    cmap=self.cmap)

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
        freq_MHz = self.S.freq_MHz
        datetimes = self.S.datetimes
        dynamic_spectra = self.S.dynamic_spectra
        pcolor_plot = ax.pcolormesh(datetimes, 
                                    freq_MHz, 
                                    dynamic_spectra, 
                                    cmap=self.cmap)
        # Format the x-axis to display time in HH:MM:SS
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.SecondLocator(interval=self.seconds_interval))
        # Assign the x and y labels with specified font size
        ax.set_ylabel('Frequency [MHz]', size=self.fsize_head)
        # Format the x and y tick labels with specified font size
        ax.tick_params(axis='x', labelsize=self.fsize)
        ax.tick_params(axis='y', labelsize=self.fsize)

