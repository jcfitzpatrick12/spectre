# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
import os
from datetime import datetime
from typing import Tuple
from matplotlib.figure import Figure
import warnings

from spectre.utils import datetime_helpers, array_helpers, fits_helpers
from spectre.utils import fits_helpers
from cfg import CONFIG
from spectre.spectrogram.PanelStack import PanelStack
from spectre.spectrogram.ComparisonStack import ComparisonStack
from spectre.json_config.FitsConfigHandler import FitsConfigHandler


class Spectrogram:
    def __init__(self, 
                 dynamic_spectra: np.ndarray,
                 time_seconds: np.ndarray, 
                 freq_MHz: np.ndarray, 
                 tag: str, 
                 chunk_start_time=None,
                 units=None,
                 microsecond_correction=0,
                 bvect=None,
                 background_interval=None):
        
        # Check if 'dynamic_spectra' is a 2D array
        if np.ndim(dynamic_spectra) != 2:
            raise ValueError(f"Expected 'dynamic_spectra' to be a 2D array, but got {np.ndim(dynamic_spectra)}D array.")

        # Check if the dimensions of 'dynamic_spectra' are consistent with 'time_seconds' and 'freq_MHz'
        if dynamic_spectra.shape[0] != len(freq_MHz):
            raise ValueError(f"Mismatch in number of columns: Expected {len(freq_MHz)}, but got {dynamic_spectra.shape[0]}.")
        
        if dynamic_spectra.shape[1] != len(time_seconds):
            raise ValueError(f"Mismatch in number of rows: Expected {len(time_seconds)}, but got {dynamic_spectra.shape[1]}.")

        self.dynamic_spectra = dynamic_spectra 

        t0_seconds = time_seconds[0]
        if t0_seconds != 0:
            raise ValueError(f"Input time_seconds array must be translated so that the first element lies at t=0. Got t0={t0_seconds} [s]")
        
        self.time_seconds = time_seconds
        self.freq_MHz = freq_MHz
        self.tag = tag

        self.shape = np.shape(dynamic_spectra)
        self.time_res_seconds = array_helpers.compute_resolution(time_seconds)
        self.freq_res_MHz = array_helpers.compute_resolution(freq_MHz)
        
        self.units = units

        self.chunk_start_datetime = None
        self.datetimes = None
        self.t0_datetime = None
        self.microsecond_correction = microsecond_correction
        # chunk_start_times are precise up to the second (due to our default time format)
        # include an optional microsecond correction
        if chunk_start_time:
            self.set_chunk_start_time(chunk_start_time)

        self.bvect = bvect
        if bvect is None:
            self.bvect = self.get_default_bvect()
        
        self.background_interval = background_interval
        self.background_indices = None
        if not self.background_interval is None:
            self.set_background(self.background_interval)


    def set_chunk_start_time(self, chunk_start_time: str):
        self.chunk_start_time = chunk_start_time
        self.chunk_start_datetime = datetime.strptime(chunk_start_time, CONFIG.default_time_format)
        self.datetimes = datetime_helpers.build_datetime_array(self.chunk_start_datetime, 
                                                                self.time_seconds,
                                                                microsecond_correction = self.microsecond_correction)
        self.t0_datetime = self.datetimes[0]


    def set_background(self, background_interval: list):
        self.background_indices = self.background_interval_to_indices(background_interval)
        start_background_index = self.background_indices[0]
        end_background_index = self.background_indices[1]
        bvect = np.nanmean(self.dynamic_spectra[:, start_background_index:end_background_index], axis=-1)
        self.bvect = bvect


    def save_to_fits(self) -> None:
        try:
            fits_config_handler = FitsConfigHandler(self.tag)
            fits_config = fits_config_handler.load_as_dict()
        except (FileNotFoundError, IOError) as e:
            warnings.warn(f"fits_config for tag {self.tag} unable to be loaded, defaulting to empty dictionary. Received error {e}")
            fits_config = {}
        chunk_parent_path = datetime_helpers.get_chunk_parent_path(self.chunk_start_time) 
        file_path = os.path.join(chunk_parent_path,f"{self.chunk_start_time}_{self.tag}.fits")
        fits_helpers.save_spectrogram(self, fits_config, file_path)
        return
    

    def integrate_over_frequency(self, background_subtract=False, normalise_integral_over_frequency=False):
            freq_Hz = self.freq_MHz * 1e-6  # Convert MHz to Hz
            I = np.nansum(self.dynamic_spectra * freq_Hz[:, np.newaxis], axis=0) # integrate over frequency

            if background_subtract:
                I = array_helpers.background_subtract(I, self.background_indices)
            if normalise_integral_over_frequency:
                I = array_helpers.normalise_peak_intensity(I)

            return I


    def get_default_bvect(self):
        return np.nanmean(self.dynamic_spectra, axis=-1)

    
    def slice_at_time(self, at_time=None, 
                      normalise_frequency_slice=False, 
                      slice_type="raw") -> Tuple[datetime|float, np.array, np.array]:

        if at_time is None:
            raise KeyError("Please specify the \"at_time\" keyword argument.")

        time_type = type(at_time)
        # Calculate the index based on the specified time identifier
        if time_type == datetime:
            if self.chunk_start_time is None:
                raise ValueError(f"With at_time specified as a datetime object, the kwarg requires that chunk_start_time is set. Currently, chunk_start_time={self.chunk_start_time}.")
            index_of_slice = datetime_helpers.find_closest_index(at_time, self.datetimes, enforce_strict_bounds = True)
            time_of_slice = self.datetimes[index_of_slice]
            
        elif time_type == float or time_type == int:
            index_of_slice = array_helpers.find_closest_index(at_time, self.time_seconds, enforce_strict_bounds = True)
            time_of_slice = self.time_seconds[index_of_slice]

        else:
            raise TypeError(f"Unexpected time type. Received {time_type} expected one of datetime, float or int.")
        
        if slice_type == "dBb":
            ds = self.dynamic_spectra_as_dBb()
        elif slice_type == "raw":
            ds = self.dynamic_spectra
        else:
            raise ValueError("Unexpected slice type. Expected one of \"raw\" or \"dBb\".")
        
        slice = ds[:, index_of_slice].copy()

        if normalise_frequency_slice and self.slice_type != "dBb":
            slice = array_helpers.normalise_peak_intensity(slice)

        # time_of_slice is distinct from that requested at input
        # time_of_slice is the EXACT time of the slice, to which the input was rounded to
        return time_of_slice, self.freq_MHz, slice


    def slice_at_frequency(self,
                           return_time_type="datetimes",  
                           at_frequency=None, 
                           slice_type="raw",
                           normalise_time_slice = False,
                           background_subtract = False):
        if at_frequency is None:
            raise ValueError(f"Must specify \"at_frequency\", received {at_frequency}")
    
        index_of_slice = array_helpers.find_closest_index(at_frequency, self.freq_MHz, enforce_strict_bounds = True)

        if return_time_type == "datetimes":
            if self.chunk_start_time is None:
                print(f"The \"datetimes\" time type requires that chunk_start_time is set. Currently, chunk_start_time={self.chunk_start_time}.")
            times = self.datetimes

        elif return_time_type == "time_seconds":
            times = self.time_seconds

        else:
            raise KeyError(f"Must specify a valid return_time_type. Got {return_time_type}, expected one of \"datetimes\" or \"time_seconds\".")

        # the requested frequency is probably not an exact bin value. Return the exact bin value.
        frequency_of_slice = self.freq_MHz[index_of_slice]

        if slice_type == "dBb":
            ds = self.dynamic_spectra_as_dBb()
        elif slice_type == "raw":
            ds = self.dynamic_spectra
        else:
            raise ValueError("Unexpected slice type. Expected one of \"raw\" or \"dBb\".")

        slice = ds[index_of_slice, :].copy()

        if background_subtract and self.slice_type != "dBb":
            slice = array_helpers.background_subtract(slice, self.background_indices)
            
        if normalise_time_slice and self.slice_type != "dBb":
            slice = array_helpers.normalise_peak_intensity(slice)

        return times, frequency_of_slice, slice 


    def dynamic_spectra_as_dBb(self):
        bvect_array = np.outer(self.bvect, np.ones(self.shape[1]))

        if self.units == "amplitude" or self.units == "digits":
            dynamic_spectra_as_dBb = 10 * np.log10(self.dynamic_spectra / bvect_array)
        elif self.units == "power":
            dynamic_spectra_as_dBb = 20 * np.log10(self.dynamic_spectra / bvect_array)
        else:
            raise ValueError(f"{self.units} unrecognised, uncertain decibel conversion!")
        
        return dynamic_spectra_as_dBb
    

    def stack_panels(self, fig: Figure, panel_types = ["raw"], **kwargs) -> None:        
        if len(panel_types) == 0:
            raise ValueError(f"At least one panel type must be specified. Received {panel_types}.")
        PanelStack(self, **kwargs).create_figure(fig, panel_types)


    def compare_with(self, fig: Figure, callisto_S, **kwargs):
        ComparisonStack().compare(fig, self, callisto_S, **kwargs)


    def background_interval_to_indices(self, background_interval: list):
        background_interval_object_type = type(background_interval)
        if not background_interval_object_type == list:
            raise TypeError(f"Background interval must be specified as a list. Received {background_interval_object_type}")

        background_interval_len = len(background_interval)
        if not len(background_interval) == 2:
            raise ValueError(f"Background interval list must be exactly two elements. Received {background_interval_len}")

        start_background = background_interval[0]
        end_background = background_interval[1]

        start_background_type = type(start_background)
        end_background_type = type(end_background)
        if not end_background_type == start_background_type:
            raise TypeError(f"All elements of the background element list must be equal.")
        
        if start_background_type == str or start_background_type == datetime:
            if self.chunk_start_time is None:
                raise ValueError(f"To specify the background as a datetime, chunk_start_time must be set. Currently, chunk_start_time = {self.chunk_start_time}.")    
        

        if start_background_type == str:
            start_background = datetime.strptime(start_background, CONFIG.default_time_format)
            end_background = datetime.strptime(end_background, CONFIG.default_time_format)
            return [datetime_helpers.find_closest_index(start_background, self.datetimes, enforce_strict_bounds = True),
                    datetime_helpers.find_closest_index(end_background, self.datetimes, enforce_strict_bounds = True)]


        elif start_background_type == datetime:
           return [datetime_helpers.find_closest_index(start_background, self.datetimes, enforce_strict_bounds = True),
                    datetime_helpers.find_closest_index(end_background, self.datetimes, enforce_strict_bounds = True)]



        elif start_background_type == int or start_background_type == float:
            return [array_helpers.find_closest_index(start_background, self.time_seconds, enforce_strict_bounds = True),
                    array_helpers.find_closest_index(end_background, self.time_seconds, enforce_strict_bounds = True)]
        

        else:
            raise TypeError(f"An unexpected error has occured. Background element type is not recognised.")
    
