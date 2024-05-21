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
                 **kwargs):
        
        # Check if 'dynamic_spectra' is a 2D array
        if np.ndim(dynamic_spectra) != 2:
            raise ValueError(f"Expected 'dynamic_spectra' to be a 2D array, but got {np.ndim(dynamic_spectra)}D array.")

        # Check if the dimensions of 'dynamic_spectra' are consistent with 'time_seconds' and 'freq_MHz'
        if dynamic_spectra.shape[0] != len(freq_MHz):
            raise ValueError(f"Mismatch in number of columns: Expected {len(freq_MHz)}, but got {dynamic_spectra.shape[0]}.")
        
        if dynamic_spectra.shape[1] != len(time_seconds):
            raise ValueError(f"Mismatch in number of rows: Expected {len(time_seconds)}, but got {dynamic_spectra.shape[1]}.")

        self.dynamic_spectra = dynamic_spectra 
        self.time_seconds = time_seconds
        self.freq_MHz = freq_MHz
        self.tag = tag

        self.shape = np.shape(dynamic_spectra)
        self.time_res_seconds = array_helpers.compute_resolution(time_seconds)
        self.freq_res_MHz = array_helpers.compute_resolution(freq_MHz)

        default_bvect = self.total_time_average()
        self.bvect = kwargs.get("bvect", default_bvect)
        self.units = kwargs.get("units", None)

        self.chunk_start_time = kwargs.get("chunk_start_time", None)
        self.chunk_start_datetime = None
        self.datetimes = None

        # chunk_start_times are precise up to the second (due to our default time format)
        # include an optional microsecond correction
        self.microsecond_correction = kwargs.get("microsecond_correction", 0)
         
        if self.chunk_start_time:
            self.chunk_start_datetime = datetime.strptime(self.chunk_start_time, CONFIG.default_time_format)
            self.datetimes = datetime_helpers.build_datetime_array(self.chunk_start_datetime, 
                                                                   time_seconds,
                                                                   microsecond_correction = self.microsecond_correction)


    def set_chunk_start_time(self, chunk_start_time):
        self.chunk_start_time = chunk_start_time
        self.chunk_start_datetime = datetime.strptime(self.chunk_start_time, CONFIG.default_time_format)
        self.datetimes = datetime_helpers.build_datetime_array(self.chunk_start_datetime, self.time_seconds)


    def save_to_fits(self) -> None:
        try:
            fits_config_handler = FitsConfigHandler(self.tag)
            fits_config = fits_config_handler.load_as_dict()
        except (FileNotFoundError, IOError) as e:
            warnings.warn(f"fits_config for tag {self.tag} unable to be loaded, defaulting to empty dictionary. Received error {e}")
            fits_config = {}
        chunk_dir = datetime_helpers.build_chunks_dir(self.chunk_start_time) 
        file_path = os.path.join(chunk_dir,f"{self.chunk_start_time}_{self.tag}.fits")
        fits_helpers.save_spectrogram(self, fits_config, file_path)
        return
    

    def integrate_over_frequency(self):
            freq_Hz = self.freq_MHz * 1e-6  # Convert MHz to Hz
            I = np.nansum(self.dynamic_spectra * freq_Hz[:, np.newaxis], axis=0)
            return I
    

    def total_time_average(self,):
        # return the spectrum averaged over all time bins
        return np.nanmean(self.dynamic_spectra, axis=-1)
    
    
    def slice_at_time(self, **kwargs) -> Tuple[datetime|float, np.array, np.array]:
        at_time = kwargs.get("at_time", None)  # in seconds

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
        
        slice = self.dynamic_spectra[:, index_of_slice].copy()
        # time_of_slice is distinct from that requested at input
        # time_of_slice is the EXACT time of the slice, to which the input was rounded to
        return time_of_slice, self.freq_MHz, slice


    def slice_at_frequency(self, **kwargs):
        at_frequency = kwargs.get("at_frequency", None)
        return_time_type = kwargs.get("return_time_type", "datetimes")

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

        slice = self.dynamic_spectra[index_of_slice, :].copy()
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
    

    def stack_panels(self, fig: Figure, **kwargs) -> None:
        panel_types = kwargs.get("panel_types", ["integrated_power", "raw"])
        if panel_types is None:
            raise ValueError(f"Panel types must be specified. Received {panel_types}.")
        
        if len(panel_types) == 0:
            raise ValueError(f"At least one panel type must be specified. Received {panel_types}.")

        PanelStack(self, **kwargs).create_figure(fig, panel_types)


    def compare_with_callisto(self, fig: Figure, callisto_S, **kwargs):
        ComparisonStack().compare_with_callisto(fig, self, callisto_S, **kwargs)