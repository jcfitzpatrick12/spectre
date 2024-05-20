from astropy.io import fits
import numpy as np
from datetime import datetime

from spectre.chunks.ChunkExt import ChunkExt
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.utils import datetime_helpers

class ChunkFits(ChunkExt):
    def __init__(self, chunk_start_time, tag: str):
        super().__init__(chunk_start_time, tag, ".fits")
    

    #load the RadioSpectrogram from the fits file.
    def load_spectrogram(self) -> Spectrogram:
        if self.exists():
            # Open the FITS file
            with fits.open(self.get_path(), mode='readonly') as hdulist:
                # Access the primary HDU
                primary_hdu = hdulist['PRIMARY']
                # Access the data part of the primary HDU
                dynamic_spectra = primary_hdu.data

                ### add a microsecond correction
                date_obs = primary_hdu.header.get('DATE-OBS', None)
                time_obs = primary_hdu.header.get('TIME-OBS', None)
                datetime_obs = datetime.strptime(f"{date_obs}T{time_obs}", "%Y/%m/%dT%H:%M:%S.%f")
                microsecond_correction = datetime_obs.microsecond
                # The index of the BINTABLE varies; commonly, it's the first extension, hence hdul[1]
                bintable_hdu = hdulist[1]
                # Access the data within the BINTABLE
                data = bintable_hdu.data
                # Extract the time and frequency arrays
                # The column names ('TIME' and 'FREQUENCY') must match those in the FITS file
                time_seconds = data['TIME'][0]
                freq_MHz = data['FREQUENCY'][0]

                # Retrieve units of the data
                units = primary_hdu.header.get('BUNIT', None)

                if units == "digits":
                    # Access the data part of the primary HDU
                    digits = primary_hdu.data  
                    digits_floats = np.array(digits, dtype = 'float')
                    # conversion as per ADC specs [see email from C. Monstein]
                    dB  = (digits_floats/255)*(2500/25)
                    dynamic_spectra_linearised = 10**(dB/10)
                    return Spectrogram(dynamic_spectra_linearised, 
                                    time_seconds, 
                                    freq_MHz, 
                                    self.tag, 
                                    chunk_start_time = self.chunk_start_time, 
                                    units = units,
                                    microsecond_correction = microsecond_correction)

                else:
                    raise ValueError(f"SPECTRE does not currently support units {units}")
                

        else:
            raise FileNotFoundError(f"Could not load spectrogram, {self.get_path()} not found.")
        


    def get_datetimes(self) -> np.ndarray:
        if self.exists():
            with fits.open(self.get_path(), mode='readonly') as hdulist:
                bintable_data = hdulist[1].data
                time_seconds = bintable_data['TIME'][0]
                return datetime_helpers.build_datetime_array(self.chunk_start_datetime, time_seconds)
        else:
            raise FileNotFoundError(f"Could not load spectrogram, {self.get_path()} not found.")


