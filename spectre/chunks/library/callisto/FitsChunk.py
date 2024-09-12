from astropy.io import fits
import numpy as np
from datetime import datetime
from typing import Tuple
from astropy.io.fits.hdu.image import PrimaryHDU
from astropy.io.fits.hdu.table import BinTableHDU
from astropy.io.fits.hdu.hdulist import HDUList

from spectre.chunks.BaseChunk import BaseChunk
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.utils import datetime_helpers

class FitsChunk(BaseChunk):
    def __init__(self, chunk_start_time: str, tag: str):
        super().__init__(chunk_start_time, tag, extension="fits")


    def read(self) -> Spectrogram:
        try:
            with fits.open(self.file_path, mode='readonly') as hdulist:
                primary_hdu = self._get_primary_hdu(hdulist)
                dynamic_spectra = self._get_dynamic_spectra(primary_hdu)
                microsecond_correction = self._get_microsecond_correction(primary_hdu)
                bintable_hdu = self._get_bintable_hdu(hdulist)
                time_seconds, freq_MHz = self._get_time_and_frequency(bintable_hdu)
                spectrum_type = self._get_spectrum_type(primary_hdu)

                if spectrum_type == "digits":
                    dynamic_spectra_linearised = self._convert_units_to_linearised(dynamic_spectra)
                    return Spectrogram(dynamic_spectra_linearised, 
                           time_seconds, 
                           freq_MHz, 
                           self.tag, 
                           chunk_start_time=self.chunk_start_time, 
                           microsecond_correction = microsecond_correction,
                           spectrum_type = spectrum_type)
                else:
                    raise ValueError(f"SPECTRE does not currently support spectrum type with BUNITS {spectrum_type}")
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not load spectrogram, {self.file_path} not found.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while reading the FITS file: {e}")


    def _get_primary_hdu(self, hdulist: HDUList) -> PrimaryHDU:
        return hdulist['PRIMARY']


    def _get_dynamic_spectra(self, primary_hdu: PrimaryHDU) -> np.ndarray:
        return primary_hdu.data


    def _get_microsecond_correction(self, primary_hdu: PrimaryHDU) -> int:
        date_obs = primary_hdu.header.get('DATE-OBS', None)
        time_obs = primary_hdu.header.get('TIME-OBS', None)
        datetime_obs = datetime.strptime(f"{date_obs}T{time_obs}", "%Y/%m/%dT%H:%M:%S.%f")
        return datetime_obs.microsecond


    def _get_bintable_hdu(self, hdulist: HDUList) -> BinTableHDU:
        return hdulist[1]


    def _get_time_and_frequency(self, bintable_hdu: BinTableHDU) -> Tuple[np.ndarray, np.ndarray]:
        data = bintable_hdu.data
        time_seconds = data['TIME'][0]
        freq_MHz = data['FREQUENCY'][0]
        return time_seconds, freq_MHz


    def _get_spectrum_type(self, primary_hdu: PrimaryHDU) -> str:
        return primary_hdu.header.get('BUNIT', None)


    def _convert_units_to_linearised(self, dynamic_spectra: np.ndarray) -> np.ndarray:
        digits_floats = np.array(dynamic_spectra, dtype='float')
        # conversion as per ADC specs [see email from C. Monstein]
        dB = (digits_floats / 255) * (2500 / 25)
        return 10 ** (dB / 10)


    def get_datetimes(self) -> np.ndarray:
        try:
            with fits.open(self.file_path, mode='readonly') as hdulist:
                bintable_data = hdulist[1].data
                time_seconds = bintable_data['TIME'][0]
                return datetime_helpers.create_datetime_array(self.chunk_start_datetime, time_seconds)
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not load spectrogram, {self.file_path} not found.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while retrieving datetime array: {e}")
