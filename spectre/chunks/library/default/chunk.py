# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from datetime import datetime, timedelta
from typing import Tuple
import numpy as np

from scipy.signal import ShortTimeFFT, get_window
from astropy.io import fits
from astropy.io.fits.hdu.image import PrimaryHDU
from astropy.io.fits.hdu.table import BinTableHDU
from astropy.io.fits.hdu.hdulist import HDUList

from spectre.chunks.chunk_register import register_chunk
from spectre.spectrograms.spectrogram import Spectrogram
from spectre.chunks.base import (
    SPECTREChunk, 
    ChunkFile
)
from spectre.exceptions import (
    ChunkFileNotFoundError
)

@register_chunk('default')
class Chunk(SPECTREChunk):
    def __init__(self, chunk_start_time: str, tag: str):
        super().__init__(chunk_start_time, tag) 
        
        self.add_file(BinChunk(self.chunk_parent_path, self.chunk_name))
        self.add_file(FitsChunk(self.chunk_parent_path, self.chunk_name))
        self.add_file(HdrChunk(self.chunk_parent_path, self.chunk_name))


    def build_spectrogram(self) -> Spectrogram:
        # fetch the raw IQ sample receiver output from the binary file
        IQ_data = self.read_file("bin")
        # and the millisecond correction from the accompanying header file
        millisecond_correction = self.read_file("hdr")
        # convert the millisecond correction to microseconds
        microsecond_correction = millisecond_correction * 1000


        # do the short time fft
        time_seconds, freq_MHz, dynamic_spectra = self.__do_STFFT(IQ_data)


        # convert all arrays to the standard type
        time_seconds = np.array(time_seconds, dtype = 'float32')
        freq_MHz = np.array(freq_MHz, dtype = 'float32')
        dynamic_spectra = np.array(dynamic_spectra, dtype = 'float32')

        return Spectrogram(dynamic_spectra, 
                           time_seconds, 
                           freq_MHz, 
                           self.tag, 
                           chunk_start_time = self.chunk_start_time, 
                           microsecond_correction = microsecond_correction,
                           spectrum_type="amplitude")

    
    def __fetch_window(self) -> np.ndarray:
        # fetch the window params and get the appropriate window
        window_type = self.capture_config.get('window_type')
        window_kwargs = self.capture_config.get('window_kwargs')
        ## note the implementation ignores the keys by necessity, due to the scipy implementation of get_window
        window_params = (window_type, *window_kwargs.values())
        window_size = self.capture_config.get('window_size')
        return get_window(window_params, window_size)

    

    def __do_STFFT(self, IQ_data: np.array) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        '''
        For reference: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.ShortTimeFFT.html
        '''
        # fetch the window
        w = self.__fetch_window()
        # find the number of samples 
        num_samples = len(IQ_data)
        # fetch the sample rate
        samp_rate = self.capture_config.get('samp_rate')
        # fetch the STFFT kwargs
        STFFT_kwargs = self.capture_config.get('STFFT_kwargs')

        # perform the short time FFT (specifying explicately keywords centered)
        SFT = ShortTimeFFT(w, fs=samp_rate, fft_mode='centered', **STFFT_kwargs)

        # set p0=0, since by convention in the STFFT docs, p=0 corresponds to the slice centred at t=0
        p0=0
        # set p1=p_ub, the index of the first slice where the "midpoint" of the window is still inside the signal
        p_ub = SFT.upper_border_begin(num_samples)[1]
        p1=p_ub
        
        signal_spectra = SFT.stft(IQ_data, p0=p0, p1=p1)  # perform the STFT (no scaling)
        # take the magnitude of the output
        dynamic_spectra = np.abs(signal_spectra)

        # build the time array
        time_seconds = SFT.t(num_samples, p0=0, p1=p1) # seconds

        # fetch the center_freq (if not specified, defaults to zero)
        center_freq = self.capture_config.get('center_freq', 0)
        # build the frequency array
        frequency_array = SFT.f + center_freq # Hz
        # convert the frequency array to MHz
        freq_MHz = frequency_array / 10**6
        return time_seconds, freq_MHz, dynamic_spectra


class BinChunk(ChunkFile):
    def __init__(self, chunk_parent_path: str, chunk_name: str):
        super().__init__(chunk_parent_path, chunk_name, "bin")

    def read(self) -> np.ndarray:
        with open(self.file_path, "rb") as fh:
            return np.fromfile(fh, dtype=np.complex64)


  
class HdrChunk(ChunkFile):
    def __init__(self, chunk_parent_path: str, chunk_name: str):
        super().__init__(chunk_parent_path, chunk_name, "hdr")


    def read(self) -> int:
        hdr_contents = self._extract_contents()
        return self._get_millisecond_correction(hdr_contents)


    def _extract_contents(self) -> np.ndarray:
        # Reads the contents of the .hdr file into a NumPy array 
        with open(self.file_path, "rb") as fh:
            return np.fromfile(fh, dtype=np.float32)


    def _get_millisecond_correction(self, hdr_contents: np.ndarray) -> int:
        # Validates that the header file contains exactly one element 
        if len(hdr_contents) != 1:
            raise ValueError(f"Expected exactly one integer in the header, but received header contents: {hdr_contents}")
        
        # Extracts and returns the millisecond correction from the file contents 
        millisecond_correction_as_float = float(hdr_contents[0])

        if not millisecond_correction_as_float.is_integer():
            raise TypeError(f"Expected integer value for millisecond correction, but got {millisecond_correction_as_float}")
        
        return int(millisecond_correction_as_float)
        



class FitsChunk(ChunkFile):
    def __init__(self, chunk_parent_path: str, chunk_name: str):
        super().__init__(chunk_parent_path, chunk_name, "fits")


    def read(self) -> Spectrogram:
        with fits.open(self.file_path, mode='readonly') as hdulist:
            primary_hdu = self._get_primary_hdu(hdulist)
            dynamic_spectra = self._get_dynamic_spectra(primary_hdu)
            spectrum_type = self._get_spectrum_type(primary_hdu)
            microsecond_correction = self._get_microsecond_correction(primary_hdu)
            bintable_hdu = self._get_bintable_hdu(hdulist)
            time_seconds, freq_MHz = self._get_time_and_frequency(bintable_hdu)

        return Spectrogram(dynamic_spectra, 
                           time_seconds, 
                           freq_MHz, 
                           self.tag, 
                           chunk_start_time=self.chunk_start_time, 
                           microsecond_correction=microsecond_correction,
                           spectrum_type = spectrum_type)


    def _get_primary_hdu(self, hdulist: HDUList) -> PrimaryHDU:
        return hdulist['PRIMARY']


    def _get_dynamic_spectra(self, primary_hdu: PrimaryHDU) -> np.ndarray:
        return primary_hdu.data


    def _get_spectrum_type(self, primary_hdu: PrimaryHDU) -> str:
        return primary_hdu.header.get('BUNIT', None)


    def _get_microsecond_correction(self, primary_hdu: PrimaryHDU) -> int:
        date_obs = primary_hdu.header.get('DATE-OBS', None)
        time_obs = primary_hdu.header.get('TIME-OBS', None)
        datetime_obs = datetime.strptime(f"{date_obs}T{time_obs}", "%Y-%m-%dT%H:%M:%S.%f")
        return datetime_obs.microsecond


    def _get_bintable_hdu(self, hdulist: HDUList) -> BinTableHDU:
        return hdulist[1]


    def _get_time_and_frequency(self, bintable_hdu: BinTableHDU) -> Tuple[np.ndarray, np.ndarray]:
        data = bintable_hdu.data
        time_seconds = data['TIME'][0]
        freq_MHz = data['FREQUENCY'][0]
        return time_seconds, freq_MHz


    def get_datetimes(self) -> np.ndarray:
        with fits.open(self.file_path, mode='readonly') as hdulist:
            bintable_data = hdulist[1].data
            time_seconds = bintable_data['TIME'][0]
            return [self.chunk_start_datetime + timedelta(seconds=t) for t in time_seconds]

