# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from astropy.io import fits
from datetime import datetime, timedelta
from typing import Tuple, Any
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LogNorm
import os


from spectre.spectrograms.array_operations import (
    find_closest_index,
    normalise_peak_intensity,
    compute_resolution,
    subtract_background,
)
from spectre.file_handlers.json.handlers import FitsConfigHandler

from spectre.cfg import (
    DEFAULT_DATETIME_FORMAT
)
from spectre.cfg import get_chunks_dir_path


class Spectrogram:
    def __init__(self, 
                 dynamic_spectra: np.ndarray[np.float32, np.float32], # holds the spectrogram data
                 times: np.ndarray[np.float32], # holds the time stamp [s] for each spectrum
                 frequencies: np.ndarray[np.float32],  # physical frequencies [Hz] for each spectral component
                 tag: str,  # the tag associated with that spectrogram
                 chunk_start_time: str = None, # (optional) the datetime (as a string) assigned to the first spectrum in the spectrogram (floored second precision)
                 microsecond_correction: int = 0, # (optional) a correction to the chunk start time
                 spectrum_type: str = None, # (optional) string which denotes the type of the spectrogram
                 background_spectrum: np.ndarray = None, # (optional) reference background spectrum, used to compute dB above background
                 background_interval: list = None): # (optional) specify an interval over which to compute the background spectrum

        # set the mandatory attributes
        self.dynamic_spectra: np.ndarray[np.float32, np.float32] = dynamic_spectra
        self.times: np.ndarray[np.float32] = times
        self.frequencies: np.ndarray[np.float32] = frequencies
        self.tag: str = tag
        # set all dependent attributes initially to None to ensure a defined state for the class
        self.time_resolution: float = None
        self.frequency_resolution: float = None
        self.spectrum_type: str = None
        self.chunk_start_time: str | None = None
        self.microsecond_correction: int = None
        self.chunk_start_datetime: datetime = None
        self.datetimes: list[datetime] = None
        self.corrected_start_datetime: datetime = None
        self.background_spectrum: np.ndarray[float] = None
        self.background_interval: list[Any] = None
        self.background_indices: list[int] = None
        self.dynamic_spectra_as_dBb: np.ndarray[float, float] = None

        # directly compute the array resolutions
        self.time_resolution = compute_resolution(times)
        self.frequency_resolution = compute_resolution(frequencies)

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
        self.chunk_start_datetime = datetime.strptime(self.chunk_start_time, DEFAULT_DATETIME_FORMAT)
        self.datetimes = [self.chunk_start_datetime + timedelta(seconds=(t + microsecond_correction*1e-6)) for t in self.times]
        self.corrected_start_datetime = self.datetimes[0]
        return


    def assign_background(self,
                          background_spectrum: np.ndarray | None = None,
                          background_interval: list | None = None) -> None:
        
        # first check if the background spectrum has been specified explictly
        if not (background_spectrum is None):
            # if it has, but the interval was also specified, raise an error (as we cannot use both)
            if not (background_interval is None):
                raise ValueError(f"Cannot specify both a background spectrum and background interval!")
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
            raise ValueError("Background interval must be a list with exactly two elements")

        start_background, end_background = self.background_interval
        background_type = type(start_background)

        if background_type != type(end_background):
            raise TypeError("All elements of the background interval list must be of the same type")

        if background_type in [str, datetime]:
            if self.chunk_start_datetime is None:
                raise ValueError("Chunk start time must be known if specifying background bounds as string or datetime")
            if background_type is str:
                start_background = datetime.strptime(start_background, DEFAULT_DATETIME_FORMAT)
                end_background = datetime.strptime(end_background, DEFAULT_DATETIME_FORMAT)
            self.background_indices = [find_closest_index(start_background, self.datetimes, enforce_strict_bounds=False),
                                       find_closest_index(end_background, self.datetimes, enforce_strict_bounds=False)]

        elif background_type in [int, float]:
            self.background_indices = [find_closest_index(start_background, self.times, enforce_strict_bounds=False),
                                       find_closest_index(end_background, self.times, enforce_strict_bounds=False)]

        else:
            raise TypeError(f"Unrecognized background interval type! Received {background_type}")

        return

    def _update_dynamic_spectra_as_dBb(self) -> None:
        # Create an artificial spectrogram where each spectrum is identically the background spectrum
        bsa = self.background_spectrum[:, np.newaxis]

        # Suppress divide by zero and invalid value warnings for this block of code
        with np.errstate(divide='ignore', invalid='ignore'):
            # Depending on the spectrum type, compute the dBb values differently
            if self.spectrum_type == "amplitude" or self.spectrum_type == "digits":
                dynamic_spectra_as_dBb = 10 * np.log10(self.dynamic_spectra / bsa)
            elif self.spectrum_type == "power":
                dynamic_spectra_as_dBb = 20 * np.log10(self.dynamic_spectra / bsa)
            else:
                raise ValueError(f"{self.spectrum_type} unrecognised, uncertain decibel conversion!")

        # Assign the result to the new attribute
        self.dynamic_spectra_as_dBb = dynamic_spectra_as_dBb
        return

    def _check_shapes(self) -> None:
        num_spectrogram_dims = np.ndim(self.dynamic_spectra)
        # Check if 'dynamic_spectra' is a 2D array
        if num_spectrogram_dims != 2:
            raise ValueError(f"Expected dynamic spectrogram to be a 2D array, but got {num_spectrogram_dims}D array")

        dynamic_spectra_shape = self.dynamic_spectra.shape
        num_freq_bins = len(self.frequencies)
        num_time_bins = len(self.times)
        # Check if the dimensions of 'dynamic_spectra' are consistent with the time and frequency arrays
        if dynamic_spectra_shape[0] != num_freq_bins:
            raise ValueError(f"Mismatch in number of columns: Expected {num_freq_bins}, but got {dynamic_spectra_shape[0]}")
        
        if dynamic_spectra_shape[1] != num_time_bins:
            raise ValueError(f"Mismatch in number of rows: Expected {num_time_bins}, but got {dynamic_spectra_shape[1]}")
        
        # Check if the shape of the background spectrum is consistent with the shape of dynamic spectrum
        num_freq_bins_in_background_spectrum = len(self.background_spectrum)
        if dynamic_spectra_shape[0] != num_freq_bins_in_background_spectrum:
            raise ValueError(f"Shape of background spectrum must be consistent with the dynamic spectrogram. Expected {dynamic_spectra_shape[0]} frequency bins, but got {num_freq_bins_in_background_spectrum}")
        return


    def save(self) -> None:
        fits_config_handler = FitsConfigHandler(self.tag)
        fits_config = fits_config_handler.read() if fits_config_handler.exists() else {}
    
        chunk_parent_path = get_chunks_dir_path(year = self.chunk_start_datetime.year,
                                                month = self.chunk_start_datetime.month,
                                                day = self.chunk_start_datetime.day)
        file_name = f"{self.chunk_start_time}_{self.tag}.fits"
        write_path = os.path.join(chunk_parent_path, file_name)
        _save_spectrogram(write_path, self, fits_config)
        return
    

    def integrate_over_frequency(self, 
                                 correct_background: bool = False, 
                                 peak_normalise: bool = False):
            
        I = np.nansum(self.dynamic_spectra * self.frequencies[:, np.newaxis], axis=0) # integrate over frequency

        if correct_background:
            I = subtract_background(I, self.background_indices)
        if peak_normalise:
            I = normalise_peak_intensity(I)
        return I
    

    def quick_plot(self, 
                time_type: str = "seconds", 
                log_norm: bool = False, 
                dBb: bool = False, 
                vmin: int = -1, 
                vmax: int = 14):
        # Create a figure
        fig, ax = plt.subplots(1)

        # Set up the time axis
        if time_type == "seconds":
            times = self.times
            ax.set_xlabel('Time [s]', size=15)
        elif time_type == "datetimes":
            if self.chunk_start_time is None:
                raise ValueError('Cannot plot with time type "datetimes" if chunk start time is not set')
            times = self.datetimes
            ax.set_xlabel('Time [UTC]', size=15)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        else:
            raise ValueError(f'Unexpected time type. Expected "seconds" or "datetimes", but received \"{time_type}\"')

        if log_norm and dBb:
            raise ValueError(f"Please specify either log_norm or dBb. Both is not supported")
        
        # Select the appropriate data and normalization
        ds = self.dynamic_spectra_as_dBb if dBb else self.dynamic_spectra
        norm = LogNorm(vmin=np.min(ds[ds > 0]), vmax=np.max(ds)) if log_norm else None

        # Assign the y label
        ax.set_ylabel('Frequency [MHz]', size=15)

        # Format the x and y tick labels
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=15)

        # Plot the dynamic spectra
        pcolor_plot = ax.pcolormesh(times, 
                                    self.frequencies*1e-6, 
                                    ds, 
                                    vmin=vmin if dBb else None, 
                                    vmax=vmax if dBb else None, 
                                    norm=norm, 
                                    cmap="gnuplot2")

        # Display the plot
        plt.show()



    def slice_at_time(self, 
                      at_time: float|int|str|datetime,
                      slice_type: str = "raw",
                      peak_normalise: bool = False) -> Tuple[datetime|float, np.array, np.array]:
        
        # it is important to note that the "at time" specified by the user likely does not correspond
        # exactly to one of the times assigned to each spectrogram. So, we compute the nearest achievable,
        # and return it from the function as output too.

        # if at_time is passed in as a string, try and parse as a datetime then proceed
        if isinstance(at_time, str):
            at_time = datetime.strptime(at_time, DEFAULT_DATETIME_FORMAT)

        if isinstance(at_time, datetime):
            if self.chunk_start_time is None:
                raise ValueError(f"With at_time specified as a datetime object, the spectrogram chunk start time must be set. Currently, chunk_start_time={self.chunk_start_time}")
            index_of_slice = find_closest_index(at_time, self.datetimes, enforce_strict_bounds = False)
            time_of_slice = self.datetimes[index_of_slice]  
        elif isinstance(at_time, float) or isinstance(at_time, int):
            index_of_slice = find_closest_index(at_time, self.times, enforce_strict_bounds = True)
            time_of_slice = self.times[index_of_slice]       
        else:
            raise TypeError(f"Unexpected time type. Received {type(at_time)} expected one of str, datetime, float or int")

        # dependent on the requested slice type, we return the dynamic spectra in the preferred units
        if slice_type == "raw":
            ds = self.dynamic_spectra
        
        elif slice_type == "dBb":
            ds = self.dynamic_spectra_as_dBb
        else:
            raise ValueError(f"Unexpected slice type. Received {slice_type} but expected \"raw\" or \"dBb\"")
        
        frequency_slice = ds[:, index_of_slice].copy() # make a copy so to preserve the spectrum on transformations of the slice

        if peak_normalise and time_of_slice != "dBb":
            frequency_slice = normalise_peak_intensity(frequency_slice)
        
        return (time_of_slice, self.frequencies, frequency_slice)

        
    def slice_at_frequency(self,
                           at_frequency: float,
                           slice_type="raw",
                           peak_normalise = False,
                           correct_background = False,
                           return_time_type: str = "datetimes") -> Tuple[float, np.array, np.array]:
        
        # it is important to note that the "at frequency" specified by the user likely does not correspond
        # exactly to one of the physical frequencies assigned to each spectral component. So, we compute the nearest achievable,
        # and return it from the function as output too.
        index_of_slice = find_closest_index(at_frequency, self.frequencies, enforce_strict_bounds = False)
        frequency_of_slice = self.frequencies[index_of_slice]

        if return_time_type == "datetimes":
            if self.chunk_start_time is None:
                raise ValueError(f"With return_time_type specified as a datetime object, the spectrogram chunk start time must be set. Currently, chunk_start_time={self.chunk_start_time}")
            times = self.datetimes
        elif return_time_type == "seconds":
            times = self.times
        else:
            raise KeyError(f"Must specify a valid return_time_type. Got {return_time_type}, expected one of \"datetimes\" or \"seconds\"")


        # dependent on the requested slice type, we return the dynamic spectra in the preferred units
        if slice_type == "raw":
            ds = self.dynamic_spectra
        
        elif slice_type == "dBb":
            ds = self.dynamic_spectra_as_dBb
        else:
            raise ValueError(f"Unexpected slice type. Received {slice_type} but expected \"raw\" or \"dBb\"")
        
        time_slice = ds[index_of_slice,:].copy() # make a copy so to preserve the spectrum on transformations of the slice

        if correct_background and self.slice_type != "dBb":
            time_slice = subtract_background(time_slice, self.background_indices)
            
        if peak_normalise and self.slice_type != "dBb":
            time_slice = subtract_background(time_slice)

        return (frequency_of_slice, times, time_slice)


def _seconds_of_day(dt: datetime) -> float:
    start_of_day = datetime(dt.year, dt.month, dt.day)
    return (dt - start_of_day).total_seconds()

# Function to create a FITS file with the specified structure
def _save_spectrogram(write_path: str, 
                      spectrogram: Spectrogram, 
                      fits_config: dict) -> None:
    if spectrogram.chunk_start_time is None:
        raise ValueError(f"Spectrogram must have a defined chunk_start_time. Received {spectrogram.chunk_start_time}")
    
    # Primary HDU with data
    primary_data = spectrogram.dynamic_spectra.astype(dtype=np.float32) 
    primary_hdu = fits.PrimaryHDU(primary_data)

    primary_hdu.header.set('SIMPLE', True, 'file does conform to FITS standard')
    primary_hdu.header.set('BITPIX', -32, 'number of bits per data pixel')
    primary_hdu.header.set('NAXIS', 2, 'number of data axes')
    primary_hdu.header.set('NAXIS1', spectrogram.dynamic_spectra.shape[1], 'length of data axis 1')
    primary_hdu.header.set('NAXIS2', spectrogram.dynamic_spectra.shape[0], 'length of data axis 2')
    primary_hdu.header.set('EXTEND', True, 'FITS dataset may contain extensions')

    # Add comments
    comments = [
        "FITS (Flexible Image Transport System) format defined in Astronomy and",
        "Astrophysics Supplement Series v44/p363, v44/p371, v73/p359, v73/p365.",
        "Contact the NASA Science Office of Standards and Technology for the",
        "FITS Definition document #100 and other FITS information."
    ]
    
    # The comments section remains unchanged since add_comment is the correct approach
    for comment in comments:
        primary_hdu.header.add_comment(comment)

    start_datetime = spectrogram.datetimes[0]
    start_date = start_datetime.strftime("%Y-%m-%d")
    start_time = start_datetime.strftime("%H:%M:%S.%f")

    end_datetime = spectrogram.datetimes[-1]
    end_date = end_datetime.strftime("%Y-%m-%d")
    end_time = end_datetime.strftime("%H:%M:%S.%f")

    primary_hdu.header.set('DATE', start_date, 'time of observation')
    primary_hdu.header.set('CONTENT', f'{start_date} dynamic spectrogram', 'title of image')
    primary_hdu.header.set('ORIGIN', f'{fits_config.get("ORIGIN")}')
    primary_hdu.header.set('TELESCOP', f'{fits_config.get("TELESCOP")} tag: {spectrogram.tag}', 'type of instrument')
    primary_hdu.header.set('INSTRUME', f'{fits_config.get("INSTRUME")}') 
    primary_hdu.header.set('OBJECT', f'{fits_config.get("OBJECT")}', 'object description')

    primary_hdu.header.set('DATE-OBS', f'{start_date}', 'date observation starts')
    primary_hdu.header.set('TIME-OBS', f'{start_time}', 'time observation starts')
    primary_hdu.header.set('DATE-END', f'{end_date}', 'date observation ends')
    primary_hdu.header.set('TIME-END', f'{end_time}', 'time observation ends')

    primary_hdu.header.set('BZERO', 0, 'scaling offset')
    primary_hdu.header.set('BSCALE', 1, 'scaling factor')
    primary_hdu.header.set('BUNIT', f"{spectrogram.spectrum_type}", 'z-axis title') 

    primary_hdu.header.set('DATAMIN', np.nanmin(spectrogram.dynamic_spectra), 'minimum element in image')
    primary_hdu.header.set('DATAMAX', np.nanmax(spectrogram.dynamic_spectra), 'maximum element in image')

    primary_hdu.header.set('CRVAL1', f'{_seconds_of_day(start_datetime)}', 'value on axis 1 at reference pixel [sec of day]')
    primary_hdu.header.set('CRPIX1', 0, 'reference pixel of axis 1')
    primary_hdu.header.set('CTYPE1', 'TIME [UT]', 'title of axis 1')
    primary_hdu.header.set('CDELT1', spectrogram.time_resolution, 'step between first and second element in x-axis')

    primary_hdu.header.set('CRVAL2', 0, 'value on axis 2 at reference pixel')
    primary_hdu.header.set('CRPIX2', 0, 'reference pixel of axis 2')
    primary_hdu.header.set('CTYPE2', 'Frequency [Hz]', 'title of axis 2')
    primary_hdu.header.set('CDELT2', spectrogram.frequency_resolution, 'step between first and second element in axis')

    primary_hdu.header.set('OBS_LAT', f'{fits_config.get("OBS_LAT")}', 'observatory latitude in degree')
    primary_hdu.header.set('OBS_LAC', 'N', 'observatory latitude code {N,S}')
    primary_hdu.header.set('OBS_LON', f'{fits_config.get("OBS_LON")}', 'observatory longitude in degree')
    primary_hdu.header.set('OBS_LOC', 'W', 'observatory longitude code {E,W}')
    primary_hdu.header.set('OBS_ALT', f'{fits_config.get("OBS_ALT")}', 'observatory altitude in meter asl')


    # Wrap arrays in an additional dimension to mimic the e-CALLISTO storage
    times_wrapped = np.array([spectrogram.times.astype(np.float32)])
    # To mimic e-Callisto storage, convert frequencies to MHz
    frequencies_MHz = spectrogram.frequencies *1e-6
    frequencies_wrapped = np.array([frequencies_MHz.astype(np.float32)])
    
    # Binary Table HDU (extension)
    col1 = fits.Column(name='TIME', format='PD', array=times_wrapped)
    col2 = fits.Column(name='FREQUENCY', format='PD', array=frequencies_wrapped)
    cols = fits.ColDefs([col1, col2])

    bin_table_hdu = fits.BinTableHDU.from_columns(cols)

    bin_table_hdu.header.set('PCOUNT', 0, 'size of special data area')
    bin_table_hdu.header.set('GCOUNT', 1, 'one data group (required keyword)')
    bin_table_hdu.header.set('TFIELDS', 2, 'number of fields in each row')
    bin_table_hdu.header.set('TTYPE1', 'TIME', 'label for field 1')
    bin_table_hdu.header.set('TFORM1', 'D', 'data format of field: 8-byte DOUBLE')
    bin_table_hdu.header.set('TTYPE2', 'FREQUENCY', 'label for field 2')
    bin_table_hdu.header.set('TFORM2', 'D', 'data format of field: 8-byte DOUBLE')
    bin_table_hdu.header.set('TSCAL1', 1, '')
    bin_table_hdu.header.set('TZERO1', 0, '')
    bin_table_hdu.header.set('TSCAL2', 1, '')
    bin_table_hdu.header.set('TZERO2', 0, '')

    # Create HDU list and write to file
    hdul = fits.HDUList([primary_hdu, bin_table_hdu])
    hdul.writeto(write_path, overwrite=True)