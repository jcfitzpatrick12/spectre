import numpy as np
import os
from datetime import datetime
from typing import Tuple
from matplotlib.figure import Figure
import warnings

from spectre.utils import datetime_helpers, array_helpers, fits_helpers
from spectre.utils import fits_helpers
from cfg import CONFIG
from spectre.spectrogram.PanelStacker import PanelStacker
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
    

    def integrated_power(self,):
        df = self.freq_res_MHz*10**-6 # Hz
        dt = self.time_res_seconds # seconds
        # find the (raw) integrated power over frequency
        integrated_power = np.sum(self.dynamic_spectra, axis=0)*df
        # normalise to integrate to one
        integrated_power/=np.trapz(integrated_power,dx=dt)
        return integrated_power
    

    def total_time_average(self,):
        # return the spectrum averaged over all time bins
        return np.nanmean(self.dynamic_spectra, axis=-1)
    
    
    def slice_at_time(self, **kwargs) -> Tuple[datetime|float, np.array, np.array]:
        at_datetime = kwargs.get("at_datetime", None)  # input datetime
        at_time = kwargs.get("at_time", None)  # in seconds

        # Validate input: only one of 'at_datetime' or 'at_time' should be specified
        if (at_datetime is not None) == (at_time is not None):
            raise KeyError("Please specify exactly one of 'at_datetime' or 'at_time'.")

        # Calculate the index based on the specified time identifier
        if at_datetime is not None:
            if self.chunk_start_time is None:
                raise ValueError(f"The \"at_datetime\" kwarg requires that chunk_start_time is set. Currently, chunk_start_time={self.chunk_start_time}.")
            index_of_slice = datetime_helpers.find_closest_index(at_datetime, self.datetimes)
            time_of_slice = self.datetimes[index_of_slice]
            
        else:
            index_of_slice = array_helpers.find_closest_index(at_time, self.time_seconds)
            time_of_slice = self.time_seconds[index_of_slice]

        return time_of_slice, self.freq_MHz, self.dynamic_spectra[:, index_of_slice]


    def slice_at_frequency(self, **kwargs):
        at_frequency = kwargs.get("at_frequency", None)
        return_time_type = kwargs.get("return_time_type", "datetimes")

        if at_frequency is None:
            raise ValueError(f"Must specify \"at_frequency\", received {at_frequency}")
    
        index_of_slice = array_helpers.find_closest_index(at_frequency, self.freq_MHz)

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

        return times, frequency_of_slice, self.dynamic_spectra[index_of_slice, :]

    def dynamic_spectra_as_dBb(self):
        bvect_array = np.outer(self.bvect, np.ones(self.shape[1]))

        if self.units == "amplitude":
            dynamic_spectra_as_dBb = 10 * np.log10(self.dynamic_spectra / bvect_array)
        elif self.units == "power":
            dynamic_spectra_as_dBb = 20 * np.log10(self.dynamic_spectra / bvect_array)
        else:
            raise ValueError(f"Units not specified, uncertain decibel conversions!")
        
        return dynamic_spectra_as_dBb
    

    def stack_panels(self, fig: Figure, panel_types: list[str], **kwargs) -> None:
        if panel_types is None:
            raise ValueError(f"Panel types must be specified. Received {panel_types}.")
        
        if len(panel_types) == 0:
            raise ValueError(f"At least one panel type must be specified. Received {panel_types}.")

        PanelStacker(self, **kwargs).create_figure(fig, panel_types)
