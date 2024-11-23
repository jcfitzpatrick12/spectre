# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime, timedelta
from typing import Tuple
import numpy as np

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

@register_chunk("fixed")
class Chunk(SPECTREChunk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        
        self.add_file(BinChunk(self.chunk_parent_path, self.chunk_name))
        self.add_file(FitsChunk(self.chunk_parent_path, self.chunk_name))
        self.add_file(HdrChunk(self.chunk_parent_path, self.chunk_name))


    def build_spectrogram(self) -> Spectrogram:
        """Create a spectrogram by performing a Short Time FFT on the IQ samples for this chunk."""
        iq_data = self.read_file("bin")
        millisecond_correction = self.read_file("hdr")

        # units conversion
        microsecond_correction = millisecond_correction * 1e3

        times, frequencies, dynamic_spectra = self.__do_STFFT(iq_data)

        # explicitly type cast data arrays to 32-bit floats
        times = np.array(times, dtype = 'float32')
        frequencies = np.array(frequencies, dtype = 'float32')
        dynamic_spectra = np.array(dynamic_spectra, dtype = 'float32')

        return Spectrogram(dynamic_spectra, 
                           times, 
                           frequencies, 
                           self.tag, 
                           chunk_start_time = self.chunk_start_time, 
                           microsecond_correction = microsecond_correction,
                           spectrum_type = "amplitude")


    def __do_STFFT(self, 
                   iq_data: np.array) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """For reference: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.ShortTimeFFT.html"""

        # set p0=0, since by convention in the STFFT docs, p=0 corresponds to the slice centred at t=0
        p0=0

        # set p1 to the index of the first slice where the "midpoint" of the window is still inside the signal
        num_samples = len(iq_data)
        p1 = self.SFT.upper_border_begin(num_samples)[1]
        
        # compute a ShortTimeFFT on the IQ samples
        complex_spectra = self.SFT.stft(iq_data, 
                                        p0 = p0, 
                                        p1 = p1) 
        
        # compute the magnitude of each spectral component
        dynamic_spectra = np.abs(complex_spectra)


        # assign a physical time to each spectrum
        times = self.SFT.t(num_samples, 
                           p0 = 0, 
                           p1 = p1)

        # assign physical frequencies to each spectral component
        frequencies = self.SFT.f + self.capture_config.get('center_freq', 0.0) 

        return times, frequencies, dynamic_spectra


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
        with open(self.file_path, "rb") as fh:
            return np.fromfile(fh, dtype=np.float32)


    def _get_millisecond_correction(self, hdr_contents: np.ndarray) -> int:
        if len(hdr_contents) != 1:
            raise ValueError(f"Expected exactly one integer in the header, but received header contents: {hdr_contents}")
        
        millisecond_correction_as_float = float(hdr_contents[0])

        if not millisecond_correction_as_float.is_integer():
            raise TypeError(f"Expected integer value for millisecond correction, but got {millisecond_correction_as_float}")
        
        return int(millisecond_correction_as_float)
        



class FitsChunk(ChunkFile):
    def __init__(self, chunk_parent_path: str, chunk_name: str):
        super().__init__(chunk_parent_path, chunk_name, "fits")


    @property
    def datetimes(self) -> np.ndarray:
        with fits.open(self.file_path, mode='readonly') as hdulist:
            bintable_data = hdulist[1].data
            times = bintable_data['TIME'][0]
            return [self.chunk_start_datetime + timedelta(seconds=t) for t in times]
        

    def read(self) -> Spectrogram:
        with fits.open(self.file_path, mode='readonly') as hdulist:
            primary_hdu = self._get_primary_hdu(hdulist)
            dynamic_spectra = self._get_dynamic_spectra(primary_hdu)
            spectrum_type = self._get_spectrum_type(primary_hdu)
            microsecond_correction = self._get_microsecond_correction(primary_hdu)
            bintable_hdu = self._get_bintable_hdu(hdulist)
            times, frequencies = self._get_time_and_frequency(bintable_hdu)

        return Spectrogram(dynamic_spectra, 
                           times, 
                           frequencies, 
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
        times = data['TIME'][0]
        frequencies_MHz = data['FREQUENCY'][0]
        frequencies = frequencies_MHz * 1e6 # convert to Hz
        return times, frequencies

