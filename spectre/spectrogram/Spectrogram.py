# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
import os
from datetime import datetime
from typing import Tuple
import warnings
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LogNorm

from spectre.utils import datetime_helpers, array_helpers, fits_helpers
from spectre.utils import fits_helpers
from cfg import CONFIG
from spectre.json_config.FitsConfigHandler import FitsConfigHandler


class Spectrogram:
    def __init__(self, 
                 dynamic_spectra: np.ndarray, # holds the spectrogram data
                 time_seconds: np.ndarray, # holds the time stamp [s] for each spectrum
                 freq_MHz: np.ndarray,  # physical frequencies [MHz] for each spectral component
                 tag: str,  # the tag associated with that spectrogram
                 chunk_start_time: str = None, # (optional) the datetime (as a string) assigned to the first spectrum in the spectrogram (floored second precision)
                 microsecond_correction: int = 0, # (optional) a correction to the chunk start time
                 spectrum_type: str = None, # (optional) string which denotes the type of the spectrogram
                 background_spectrum: np.ndarray = None, # (optional) reference background spectrum, used to compute dB above background
                 background_interval: list = None): # (optional) specify an interval over which to compute the background spectrum

        # set the mandatory attributes
        self.dynamic_spectra = dynamic_spectra
        self.time_seconds = time_seconds
        self.freq_MHz = freq_MHz
        self.tag = tag
        # set all dependent attributes initially to None to ensure a defined state for the class
        self.time_res_seconds = None
        self.freq_res_MHz = None
        self.spectrum_type = None
        self.chunk_start_time = None
        self.microsecond_correction = None
        self.chunk_start_datetime = None
        self.datetimes = None
        self.corrected_start_datetime = None
        self.background_spectrum = None
        self.background_interval = None
        self.background_indices = None
        self.dynamic_spectra_as_dBb = None

        # directly compute the array resolutions
        self.time_res_seconds = array_helpers.compute_resolution(time_seconds)
        self.freq_res_MHz = array_helpers.compute_resolution(freq_MHz)

        # set the spectrum type based on constructor input
        self.spectrum_type = spectrum_type

        # if the user has passed in a chunk start time via kwargs, assign datetimes to each spectrum
        if chunk_start_time:
            self.assign_datetimes(chunk_start_time,
                                  microsecond_correction)
        
        # with the datetimes specified (if required), we can now update the background spectrum based on constructor inputs
        self.assign_background(background_spectrum = background_spectrum,
                               background_interval = background_interval)
        
        self._check_shapes()
        return
    

    def assign_datetimes(self, 
                         chunk_start_time: str,
                         microsecond_correction: float = 0) -> None:
        self.chunk_start_time = chunk_start_time
        self.microsecond_correction = microsecond_correction
        self.chunk_start_datetime = datetime.strptime(self.chunk_start_time, CONFIG.default_time_format)
        self.datetimes = datetime_helpers.create_datetime_array(self.chunk_start_datetime, 
                                                                self.time_seconds,
                                                                microsecond_correction = microsecond_correction)
        self.corrected_start_datetime = self.datetimes[0]
        return


    def assign_background(self,
                          background_spectrum: np.ndarray = None,
                          background_interval: list = None) -> None:
        
        # first check if the background spectrum has been specified explictly
        if not (background_spectrum is None):
            # if it has, but the interval was also specified, raise an error (as we cannot use both)
            if not (background_interval is None):
                raise ValueError(f"Cannot specify both background spectrum and background interval! Background must be assigned either explictly or via the interval.")
            # otherwise, set the background spectrum and proceed
            self.background_spectrum = background_spectrum

        # if the background spectrum was not set explictly, check instead for the background interval
        elif not (background_interval is None):
            self.background_interval = background_interval
            # if the background interval is specified, we can set the background indices
            self._set_background_indices()
            # then set the background spectrum based off the specified interval
            self._set_background_spectrum_from_interval()

        # if neither has been specified, compute the default by averaging over the entire spectrogram
        else:
            self._set_background_spectrum_as_default()
            
        self._check_shapes()   
        # with the background spectrum in a defined state, update the dynamic spectra as dBb
        self._update_dynamic_spectra_as_dBb()
        return
    

    def _set_background_spectrum_from_interval(self) -> None:
        start_index, end_index = self.background_indices
        self.background_spectrum = np.nanmean(self.dynamic_spectra[:, start_index:end_index+1], axis=-1)
        return
    

    def _set_background_spectrum_as_default(self) -> None:
        self.background_spectrum = np.nanmean(self.dynamic_spectra, axis=-1)
    

    def _set_background_indices(self) -> list[int]:
        if not isinstance(self.background_interval, list) or len(self.background_interval) != 2:
            raise ValueError("Background interval must be a list with exactly two elements.")

        start_background, end_background = self.background_interval
        background_type = type(start_background)

        if background_type != type(end_background):
            raise TypeError("All elements of the background interval list must be of the same type.")

        if background_type in [str, datetime]:
            if self.chunk_start_datetime is None:
                raise ValueError("Chunk start time must be known if specifying background bounds as string or datetime.")
            if background_type is str:
                start_background = datetime.strptime(start_background, CONFIG.default_time_format)
                end_background = datetime.strptime(end_background, CONFIG.default_time_format)
            self.background_indices = [datetime_helpers.find_closest_index(start_background, self.datetimes, enforce_strict_bounds=False),
                                       datetime_helpers.find_closest_index(end_background, self.datetimes, enforce_strict_bounds=False)]

        elif background_type in [int, float]:
            self.background_indices = [array_helpers.find_closest_index(start_background, self.time_seconds, enforce_strict_bounds=False),
                                       array_helpers.find_closest_index(end_background, self.time_seconds, enforce_strict_bounds=False)]

        else:
            raise TypeError(f"Unrecognized background interval type! Received {background_type}.")

        return

    def _update_dynamic_spectra_as_dBb(self) -> None:
        # for ease of computation, create a background spectrum array (bsa) of the same shape as the input dynamic spectra
        # except each spectrum is identically the background spectrum
        bsa = np.outer(self.background_spectrum, np.ones(self.dynamic_spectra.shape[1])) 
        # depending on the spectrum type, we compute the dBb values differently:
        if self.spectrum_type == "amplitude" or self.spectrum_type == "digits":
            dynamic_spectra_as_dBb = 10 * np.log10(self.dynamic_spectra / bsa)
        elif self.spectrum_type == "power":
            dynamic_spectra_as_dBb = 20 * np.log10(self.dynamic_spectra / bsa)
        else:
            raise ValueError(f"{self.spectrum_type} unrecognised, uncertain decibel conversion!")
        
        self.dynamic_spectra_as_dBb = dynamic_spectra_as_dBb
        return
    

    def _check_shapes(self) -> None:
        num_spectrogram_dims = np.ndim(self.dynamic_spectra)
        # Check if 'dynamic_spectra' is a 2D array
        if num_spectrogram_dims != 2:
            raise ValueError(f"Expected 'dynamic_spectra' to be a 2D array, but got {num_spectrogram_dims}D array.")

        dynamic_spectra_shape = self.dynamic_spectra.shape
        num_freq_bins = len(self.freq_MHz)
        num_time_bins = len(self.time_seconds)
        # Check if the dimensions of 'dynamic_spectra' are consistent with 'time_seconds' and 'freq_MHz'
        if dynamic_spectra_shape[0] != num_freq_bins:
            raise ValueError(f"Mismatch in number of columns: Expected {num_freq_bins}, but got {dynamic_spectra_shape[0]}.")
        
        if dynamic_spectra_shape[1] != num_time_bins:
            raise ValueError(f"Mismatch in number of rows: Expected {num_time_bins}, but got {dynamic_spectra_shape[1]}.")
        
        # Check if the shape of the background spectrum is consistent with the shape of dynamic spectrum
        num_freq_bins_in_background_spectrum = len(self.background_spectrum)
        if dynamic_spectra_shape[0] != num_freq_bins_in_background_spectrum:
            raise ValueError(f"Shape of background spectrum must be consistent with dynamic spectra. Expected {dynamic_spectra_shape[0]} frequency bins, got {num_freq_bins_in_background_spectrum}")
        return


    def save_to_fits(self) -> None:
        try:
            fits_config_handler = FitsConfigHandler(self.tag)
            fits_config = fits_config_handler.load_as_dict()
        except (FileNotFoundError, IOError) as e:
            warnings.warn(f"fits_config for tag {self.tag} unable to be loaded, defaulting to empty dictionary. Received error {e}")
            fits_config = {}
        chunk_parent_path = datetime_helpers.get_chunk_parent_path(self.chunk_start_time) 
        file_path = os.path.join(chunk_parent_path, f"{self.chunk_start_time}_{self.tag}.fits")
        fits_helpers.save_spectrogram(self, fits_config, file_path)
        return
    

    def integrate_over_frequency(self, 
                                 background_subtract: bool = False, 
                                 peak_normalise: bool = False):
            
        freq_Hz = self.freq_MHz * 1e-6  # Convert MHz to Hz
        I = np.nansum(self.dynamic_spectra * freq_Hz[:, np.newaxis], axis=0) # integrate over frequency

        if background_subtract:
            I = array_helpers.background_subtract(I, self.background_indices)
        if peak_normalise:
            I = array_helpers.normalise_peak_intensity(I)
        return I
    

    def quick_plot(self,
                   time_type: str = "time_seconds",
                   log_norm: bool = False):
        # create a figure
        fig, ax = plt.subplots(1)

        if time_type == "time_seconds":
            times = self.time_seconds
            ax.set_xlabel(f'Time [s]', size=15)
        # If the chunk start time is specified, plot with datetimes
        elif time_type == "datetimes":
            if self.chunk_start_time is None:
                raise ValueError(f"Cannot plot with time type \"datetimes\" if chunk start time is not set.")
            times = self.datetimes
            ax.set_xlabel(f'Time [UTC]', size=15)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        else:
            raise ValueError(f"Unexpected time type. Expected \"time_seconds\" or \"datetimes\", but received {time_type}.")

        if log_norm:
            norm = LogNorm(vmin=np.min(self.dynamic_spectra[self.dynamic_spectra > 0]), vmax=np.max(self.dynamic_spectra))
        else:
            norm = None

        # Assign the x and y labels with specified font size
        ax.set_ylabel('Frequency [MHz]', size=15)
        # Format the x and y tick labels with specified font size
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=15)

        pcolor_plot = ax.pcolormesh(times, 
                                    self.freq_MHz, 
                                    self.dynamic_spectra, 
                                    norm=norm,
                                    cmap="gnuplot2")

        plt.show()
        return


    def slice_at_time(self, 
                      at_time: float|int|str|datetime,
                      slice_type: str = "raw",
                      peak_normalise: bool = False) -> Tuple[datetime|float, np.array, np.array]:
        
        # it is important to note that the "at time" specified by the user likely does not correspond
        # exactly to one of the times assigned to each spectrogram. So, we compute the nearest achievable,
        # and return it from the function as output too.

        # if at_time is passed in as a string, try and parse as a datetime then proceed
        if isinstance(at_time, str):
            at_time = datetime.strptime(at_time, CONFIG.default_time_format)

        if isinstance(at_time, datetime):
            if self.chunk_start_time is None:
                raise ValueError(f"With at_time specified as a datetime object, the spectrogram chunk start time must be set. Currently, chunk_start_time={self.chunk_start_time}.")
            index_of_slice = datetime_helpers.find_closest_index(at_time, self.datetimes, enforce_strict_bounds = False)
            time_of_slice = self.datetimes[index_of_slice]  
        elif isinstance(at_time, float) or isinstance(at_time, int):
            index_of_slice = array_helpers.find_closest_index(at_time, self.time_seconds, enforce_strict_bounds = True)
            time_of_slice = self.time_seconds[index_of_slice]       
        else:
            raise TypeError(f"Unexpected time type. Received {type(at_time)} expected one of str, datetime, float or int.")

        # dependent on the requested slice type, we return the dynamic spectra in the preferred units
        if slice_type == "raw":
            ds = self.dynamic_spectra
        
        elif slice_type == "dBb":
            ds = self.dynamic_spectra_as_dBb
        else:
            raise ValueError(f"Unexpected slice type. Received {slice_type} but expected \"raw\" or \"dBb\".")
        
        frequency_slice = ds[:, index_of_slice].copy() # make a copy so to preserve the spectrum on transformations of the slice

        if peak_normalise and time_of_slice != "dBb":
            frequency_slice = array_helpers.normalise_peak_intensity(frequency_slice)
        
        return (time_of_slice, self.freq_MHz, frequency_slice)

        
    def slice_at_frequency(self,
                           at_frequency: float,
                           slice_type="raw",
                           peak_normalise = False,
                           background_subtract = False,
                           return_time_type: str = "datetimes") -> Tuple[float, np.array, np.array]:
        
        # it is important to note that the "at frequency" specified by the user likely does not correspond
        # exactly to one of the physical frequencies assigned to each spectral component. So, we compute the nearest achievable,
        # and return it from the function as output too.
        index_of_slice = array_helpers.find_closest_index(at_frequency, self.freq_MHz, enforce_strict_bounds = False)
        frequency_of_slice = self.freq_MHz[index_of_slice]

        if return_time_type == "datetimes":
            if self.chunk_start_time is None:
                raise ValueError(f"With return_time_type specified as a datetime object, the spectrogram chunk start time must be set. Currently, chunk_start_time={self.chunk_start_time}")
            times = self.datetimes
        elif return_time_type == "time_seconds":
            times = self.time_seconds
        else:
            raise KeyError(f"Must specify a valid return_time_type. Got {return_time_type}, expected one of \"datetimes\" or \"time_seconds\".")


        # dependent on the requested slice type, we return the dynamic spectra in the preferred units
        if slice_type == "raw":
            ds = self.dynamic_spectra
        
        elif slice_type == "dBb":
            ds = self.dynamic_spectra_as_dBb
        else:
            raise ValueError(f"Unexpected slice type. Received {slice_type} but expected \"raw\" or \"dBb\".")
        
        time_slice = ds[index_of_slice,:].copy() # make a copy so to preserve the spectrum on transformations of the slice

        if background_subtract and self.slice_type != "dBb":
            time_slice = array_helpers.background_subtract(slice, self.background_indices)
            
        if peak_normalise and self.slice_type != "dBb":
            time_slice = array_helpers.normalise_peak_intensity(slice)

        return (frequency_of_slice, times, time_slice)

    
    # TO BE REVISED # 
    # def stack_panels(self, fig: Figure, panel_types = ["raw"], **kwargs) -> None:        
    #     return


    # def compare_with(self, fig: Figure, callisto_S, **kwargs):
    #     return
