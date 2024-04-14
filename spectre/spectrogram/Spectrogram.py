import numpy as np
import os
from datetime import datetime
from typing import Tuple

from spectre.utils import datetime_helpers, array_helpers, fits_helpers
from spectre.utils import fits_helpers
from spectre.cfg import CONFIG


class Spectrogram:
    def __init__(self, 
                 mags: np.ndarray,
                #  scaled_to: str,
                 time_seconds: np.ndarray, 
                 freq_MHz: np.ndarray, 
                 chunk_start_time: str, 
                 tag: str, 
                 chunks_dir: str,
                 **kwargs):
        
        # Check if 'mags' is a 2D array
        if np.ndim(mags) != 2:
            raise ValueError(f"Expected 'mags' to be a 2D array, but got {np.ndim(mags)}D array.")

        # Check if the dimensions of 'mags' are consistent with 'time_seconds' and 'freq_MHz'
        if mags.shape[0] != len(freq_MHz):
            raise ValueError(f"Mismatch in number of columns: Expected {len(freq_MHz)}, but got {mags.shape[0]}.")
        
        if mags.shape[1] != len(time_seconds):
            raise ValueError(f"Mismatch in number of rows: Expected {len(time_seconds)}, but got {mags.shape[1]}.")

        self.mags = mags 
        self.time_seconds = time_seconds
        self.freq_MHz = freq_MHz
        self.time_res_seconds = array_helpers.compute_resolution(time_seconds)
        self.freq_res_MHz = array_helpers.compute_resolution(freq_MHz)

        self.chunk_start_time = chunk_start_time
        self.tag = tag
        self.chunks_dir = datetime_helpers.build_chunks_dir(self.chunk_start_time, chunks_dir) 
        self.bvect = kwargs.get("bvect", None)

        self.chunk_start_datetime = datetime.strptime(self.chunk_start_time, CONFIG.default_time_format)
        self.datetimes = datetime_helpers.build_datetime_array(self.chunk_start_datetime, time_seconds)



    def get_path(self) -> str:
        return os.path.join(self.chunks_dir,f"{self.chunk_start_time}_{self.tag}.fits")


    def save_to_fits(self, fits_config: dict) -> None:
        fits_helpers.save_spectrogram(self, fits_config, self.get_path())
        return
    

    def integrated_power(self,):
        df = self.freq_res_MHz*10**-6 # Hz
        dt = self.time_res_seconds # seconds
        # find the (raw) integrated power over frequency
        integrated_power = np.sum(self.mags, axis=0)*df
        # normalise to integrate to one
        integrated_power/=np.trapz(integrated_power,dx=dt)
        return integrated_power
    

    def total_time_average(self,):
        # return the spectrum averaged over all time bins
        return np.nanmean(self.mags, axis=-1)
    
    
    def slice_at_time(self, **kwargs) -> Tuple[datetime|float, np.array, np.array]:
        at_datetime = kwargs.get("at_datetime", None)  # input datetime
        at_time = kwargs.get("at_time", None)  # in seconds

        # Validate input: only one of 'at_datetime' or 'at_time' should be specified
        if (at_datetime is not None) == (at_time is not None):
            raise KeyError("Please specify exactly one of 'at_datetime' or 'at_time'.")

        # Calculate the index based on the specified time identifier
        if at_datetime is not None:
            index_of_slice = datetime_helpers.find_closest_index(at_datetime, self.datetimes)
            time_of_slice = self.datetimes[index_of_slice]
        else:
            index_of_slice = array_helpers.find_closest_index(at_time, self.time_seconds)
            time_of_slice = self.time_seconds[index_of_slice]

        return time_of_slice, self.freq_MHz, self.mags[:, index_of_slice]


    def slice_at_frequency(self, **kwargs):
        at_frequency = kwargs.get("at_frequency", None)
        return_time_type = kwargs.get("return_time_type", "datetimes")

        if at_frequency is None:
            raise ValueError(f"Must specify \"at_frequency\", received {at_frequency}")
    
        index_of_slice = array_helpers.find_closest_index(at_frequency, self.freq_MHz)
        if return_time_type == "datetimes":
            times = self.datetimes
        elif return_time_type == "time_seconds":
            times = self.time_seconds
        else:
            raise KeyError(f"Must specify a valid return_time_type. Got {return_time_type}, expected one of \"datetimes\" or \"time_seconds\".")

        # the requested frequency is probably not an exact bin value. Return the exact bin value.
        frequency_of_slice = self.freq_MHz[index_of_slice]

        return times, frequency_of_slice, self.mags[index_of_slice, :]

    