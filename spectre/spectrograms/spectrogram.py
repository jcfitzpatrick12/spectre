# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from typing import Optional
from warnings import warn
from datetime import datetime, timedelta
from dataclasses import dataclass

import numpy as np
from astropy.io import fits

from spectre.file_handlers.json import FitsConfigHandler
from spectre.cfg import DEFAULT_DATETIME_FORMAT, get_chunks_dir_path
from spectre.spectrograms.array_operations import (
    find_closest_index,
    normalise_peak_intensity,
    compute_resolution,
    compute_range,
    subtract_background,
)

@dataclass
class FrequencyCut:
    time: float | datetime
    frequencies: np.ndarray
    cut: np.ndarray
    spectrum_type: str


@dataclass
class TimeCut:
    frequency: float
    times: np.ndarray
    cut: np.ndarray
    spectrum_type: str
    

class Spectrogram:
    def __init__(self, 
                 dynamic_spectra: np.ndarray, # holds the spectrogram data
                 times: np.ndarray, # holds the time stamp [s] for each spectrum
                 frequencies: np.ndarray,  # physical frequencies [Hz] for each spectral component
                 tag: str,
                 chunk_start_time: Optional[str] = None, 
                 microsecond_correction: int = 0, 
                 spectrum_type: Optional[str] = None,
                 start_background: Optional[str] = None, 
                 end_background: Optional[str] = None): 
        
        # dynamic spectra
        self._dynamic_spectra = dynamic_spectra
        self._dynamic_spectra_as_dBb: Optional[np.ndarray] = None # cache

        # assigned times and frequencies
        self._times = times
        self._datetimes: Optional[list[datetime]] = None # cache
        self._frequencies = frequencies

        # general metadata
        self._tag = tag
        self._chunk_start_time = chunk_start_time
        self._chunk_start_datetime: Optional[datetime] = None # cache
        self._microsecond_correction = microsecond_correction
        self._spectrum_type = spectrum_type

        # background metadata     
        self._background_spectrum: Optional[np.ndarray] = None # cache
        self._start_background = start_background
        self._end_background = end_background
        self._start_background_index = 0 # by default
        self._end_background_index = self.num_times # by default
        self._check_shapes()


    @property
    def dynamic_spectra(self) -> np.ndarray:
        return self._dynamic_spectra
    

    @property
    def times(self) -> np.ndarray:
        return self._times
    
    
    @property
    def num_times(self) -> int:
        return len(self._times)
    

    @property
    def time_resolution(self) -> float:
        return compute_resolution(self._times)
    

    @property
    def time_range(self) -> float:
        return compute_range(self._times)
    

    @property
    def datetimes(self) -> list[datetime]:
        if self._datetimes is None:
            self._datetimes = [self.chunk_start_datetime + timedelta(seconds=(t + self.microsecond_correction*1e-6)) for t in self._times]
        return self._datetimes
    

    @property
    def frequencies(self) -> np.ndarray:
        return self._frequencies


    @property
    def num_frequencies(self) -> int:
        return len(self._frequencies)
    
    
    @property
    def frequency_resolution(self) -> float:
        return compute_resolution(self._frequencies)
    

    @property
    def frequency_range(self) -> float:
        return compute_range(self._frequencies)
    

    @property
    def tag(self) -> str:
        return self._tag
    

    @property
    def chunk_start_time(self) -> str:
        if self._chunk_start_time is None:
            raise AttributeError(f"Chunk start time has not been set.")
        return self._chunk_start_time
    

    @property
    def chunk_start_datetime(self) -> datetime:
        if self._chunk_start_datetime is None:
            self._chunk_start_datetime = datetime.strptime(self.chunk_start_time, DEFAULT_DATETIME_FORMAT)
        return self._chunk_start_datetime


    @property
    def microsecond_correction(self) -> int:
        return self._microsecond_correction
    

    @property
    def spectrum_type(self) -> Optional[str]:
        return self._spectrum_type
    

    @property
    def start_background(self) -> Optional[str]:
        return self._start_background
    

    @property
    def end_background(self) -> Optional[str]:
        return self._end_background
    
    
    @property
    def background_spectrum(self) -> np.ndarray:
        if self._background_spectrum is None:
            self._background_spectrum = np.nanmean(self._dynamic_spectra[:, self._start_background_index:self._end_background_index+1], 
                                               axis=-1)
        return self._background_spectrum
    

    @property
    def dynamic_spectra_as_dBb(self) -> np.ndarray:
        if self._dynamic_spectra_as_dBb is None:
            # Create an artificial spectrogram where each spectrum is identically the background spectrum
            background_spectra = self.background_spectrum[:, np.newaxis]
            # Suppress divide by zero and invalid value warnings for this block of code
            with np.errstate(divide='ignore'):
                # Depending on the spectrum type, compute the dBb values differently
                if self._spectrum_type == "amplitude" or self._spectrum_type == "digits":
                    self._dynamic_spectra_as_dBb = 10 * np.log10(self._dynamic_spectra / background_spectra)
                elif self._spectrum_type == "power":
                    self._dynamic_spectra_as_dBb = 20 * np.log10(self._dynamic_spectra / background_spectra)
                else:
                    raise NotImplementedError(f"{self.spectrum_type} unrecognised, uncertain decibel conversion!")
        return self._dynamic_spectra_as_dBb  
    
    
    def set_background(self, 
                       start_background: str, 
                       end_background: str) -> None:
        """Public setter for start and end of the background"""
        self._dynamic_spectra_as_dBb = None # reset cache
        self._background_spectrum = None # reset cache
        self._start_background = start_background
        self._end_background = end_background
        self._update_background_indices_from_interval()
    
    
    
    def _update_background_indices_from_interval(self) -> None:
        start_background = datetime.strptime(self._start_background, DEFAULT_DATETIME_FORMAT)
        self._start_background_index = find_closest_index(start_background, 
                                                          self.datetimes, 
                                                          enforce_strict_bounds=False)
        
        end_background = datetime.strptime(self._end_background, DEFAULT_DATETIME_FORMAT)
        self._end_background_index = find_closest_index(end_background, 
                                                        self.datetimes, 
                                                        enforce_strict_bounds=False)


    def _check_shapes(self) -> None:
        num_spectrogram_dims = np.ndim(self._dynamic_spectra)
        # Check if 'dynamic_spectra' is a 2D array
        if num_spectrogram_dims != 2:
            raise ValueError(f"Expected dynamic spectrogram to be a 2D array, but got {num_spectrogram_dims}D array")
        dynamic_spectra_shape = self.dynamic_spectra.shape
        # Check if the dimensions of 'dynamic_spectra' are consistent with the time and frequency arrays
        if dynamic_spectra_shape[0] != self.num_frequencies:
            raise ValueError(f"Mismatch in number of frequency bins: Expected {self.num_frequencies}, but got {dynamic_spectra_shape[0]}")
        
        if dynamic_spectra_shape[1] != self.num_times:
            raise ValueError(f"Mismatch in number of time bins: Expected {self.num_times}, but got {dynamic_spectra_shape[1]}")
        

    def save(self) -> None:
        fits_config_handler = FitsConfigHandler(self._tag)
        fits_config = fits_config_handler.read() if fits_config_handler.exists  else {}

        chunk_start_datetime = self.chunk_start_datetime
        chunk_parent_path = get_chunks_dir_path(year = chunk_start_datetime.year,
                                                month = chunk_start_datetime.month,
                                                day = chunk_start_datetime.day)
        file_name = f"{self.chunk_start_time}_{self._tag}.fits"
        write_path = os.path.join(chunk_parent_path, file_name)
        _save_spectrogram(write_path, self, fits_config)
    

    def integrate_over_frequency(self, 
                                 correct_background: bool = False, 
                                 peak_normalise: bool = False) -> np.ndarray[np.float32]:
        
        # integrate over frequency
        I = np.trapz(self._dynamic_spectra, self._frequencies, axis=0)

        if correct_background:
            I = subtract_background(I, 
                                    self._start_background_index, 
                                    self._end_background_index)
        if peak_normalise:
            I = normalise_peak_intensity(I)
        return I


    def get_frequency_cut(self, 
                          at_time: float | str,
                          dBb: bool = False,
                          peak_normalise: bool = False) -> FrequencyCut:
        
        # it is important to note that the "at time" specified by the user likely does not correspond
        # exactly to one of the times assigned to each spectrogram. So, we compute the nearest achievable,
        # and return it from the function as output too.
        if isinstance(at_time, str):
            at_time = datetime.strptime(at_time, DEFAULT_DATETIME_FORMAT)
            index_of_cut = find_closest_index(at_time, 
                                              self.datetimes, 
                                              enforce_strict_bounds = True)
            time_of_cut = self.datetimes[index_of_cut]  

        if isinstance(at_time, float):
            index_of_cut = find_closest_index(at_time, 
                                              self._times, 
                                              enforce_strict_bounds = True)
            time_of_cut = self.times[index_of_cut]
        
        if dBb:
            ds = self.dynamic_spectra_as_dBb
        else:
            ds = self._dynamic_spectra
        
        cut = ds[:, index_of_cut].copy() # make a copy so to preserve the spectrum on transformations of the cut

        if dBb:
            if peak_normalise:
                warn("Ignoring frequency cut normalisation, since dBb units have been specified")
        else:
            if peak_normalise:
                cut = normalise_peak_intensity(cut)
        
        return FrequencyCut(time_of_cut, 
                            self._frequencies, 
                            cut, 
                            self._spectrum_type)

        
    def get_time_cut(self,
                     at_frequency: float,
                     dBb: bool = False,
                     peak_normalise = False, 
                     correct_background = False, 
                     return_time_type: str = "seconds") -> TimeCut:
        
        # it is important to note that the "at frequency" specified by the user likely does not correspond
        # exactly to one of the physical frequencies assigned to each spectral component. So, we compute the nearest achievable,
        # and return it from the function as output too.
        index_of_cut = find_closest_index(at_frequency, 
                                          self._frequencies, 
                                          enforce_strict_bounds = True)
        frequency_of_cut = self.frequencies[index_of_cut]

        if return_time_type == "datetimes":
            times = self.datetimes
        elif return_time_type == "seconds":
            times = self.times
        else:
            raise ValueError(f"Invalid return_time_type. Got {return_time_type}, expected one of 'datetimes' or 'seconds'")

        # dependent on the requested cut type, we return the dynamic spectra in the preferred units
        if dBb:
            ds = self.dynamic_spectra_as_dBb
        else:
            ds = self.dynamic_spectra
        
        cut = ds[index_of_cut,:].copy() # make a copy so to preserve the spectrum on transformations of the cut

        # Warn if dBb is used with background correction or peak normalisation
        if dBb:
            if correct_background or peak_normalise:
                warn("Ignoring time cut normalisation, since dBb units have been specified")
        else:
            # Apply background correction if required
            if correct_background:
                cut = subtract_background(cut, 
                                          self._start_background_index,
                                          self._end_background_index)
            
            # Apply peak normalisation if required
            if peak_normalise:
                cut = normalise_peak_intensity(cut)

        return TimeCut(frequency_of_cut, 
                         times, 
                         cut,
                         self.spectrum_type)
    

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
