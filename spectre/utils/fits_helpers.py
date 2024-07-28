# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from astropy.io import fits
from datetime import datetime

from spectre.utils import datetime_helpers



# Function to create a FITS file with the specified structure
def save_spectrogram(S, fits_config: dict, path_to_fits: str):

    if S.chunk_start_time is None:
        raise ValueError(f"Spectrogram must have a defined chunk_start_time. Received {S.chunk_start_time}.")
    
    # Primary HDU with data
    primary_data = S.dynamic_spectra.astype(dtype=np.float64) 
    primary_hdu = fits.PrimaryHDU(primary_data)

    primary_hdu.header.set('SIMPLE', True, 'file does conform to FITS standard')
    primary_hdu.header.set('BITPIX', -64, 'number of bits per data pixel')
    primary_hdu.header.set('NAXIS', 2, 'number of data axes')
    primary_hdu.header.set('NAXIS1', S.dynamic_spectra.shape[1], 'length of data axis 1')
    primary_hdu.header.set('NAXIS2', S.dynamic_spectra.shape[0], 'length of data axis 2')
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

    start_datetime = S.datetimes[0]
    start_date = start_datetime.strftime("%Y-%m-%d")
    start_time = start_datetime.strftime("%H:%M:%S.%f")

    end_datetime = S.datetimes[-1]
    end_date = end_datetime.strftime("%Y-%m-%d")
    end_time = end_datetime.strftime("%H:%M:%S.%f")

    primary_hdu.header.set('DATE', start_date, 'time of observation')
    primary_hdu.header.set('CONTENT', f'{start_date} dynamic spectrogram', 'title of image')
    primary_hdu.header.set('ORIGIN', f'{fits_config.get("ORIGIN")}')
    primary_hdu.header.set('TELESCOP', f'{fits_config.get("TELESCOP")} tag: {S.tag}', 'type of instrument')
    primary_hdu.header.set('INSTRUME', f'{fits_config.get("INSTRUME")}') 
    primary_hdu.header.set('OBJECT', f'{fits_config.get("OBJECT")}', 'object description')

    primary_hdu.header.set('DATE-OBS', f'{start_date}', 'date observation starts')
    primary_hdu.header.set('TIME-OBS', f'{start_time}', 'time observation starts')
    primary_hdu.header.set('DATE-END', f'{end_date}', 'date observation ends')
    primary_hdu.header.set('TIME-END', f'{end_time}', 'time observation ends')

    primary_hdu.header.set('BZERO', 0, 'scaling offset')
    primary_hdu.header.set('BSCALE', 1, 'scaling factor')
    primary_hdu.header.set('BUNIT', f"{S.spectrum_type}", 'z-axis title') 

    primary_hdu.header.set('DATAMIN', np.nanmin(S.dynamic_spectra), 'minimum element in image')
    primary_hdu.header.set('DATAMAX', np.nanmax(S.dynamic_spectra), 'maximum element in image')

    primary_hdu.header.set('CRVAL1', f'{datetime_helpers.seconds_of_day(start_datetime)}', 'value on axis 1 at reference pixel [sec of day]')
    primary_hdu.header.set('CRPIX1', 0, 'reference pixel of axis 1')
    primary_hdu.header.set('CTYPE1', 'TIME [UT]', 'title of axis 1')
    primary_hdu.header.set('CDELT1', S.time_res_seconds, 'step between first and second element in x-axis')

    primary_hdu.header.set('CRVAL2', 0, 'value on axis 2 at reference pixel')
    primary_hdu.header.set('CRPIX2', 0, 'reference pixel of axis 2')
    primary_hdu.header.set('CTYPE2', 'Frequency [MHz]', 'title of axis 2')
    primary_hdu.header.set('CDELT2', S.freq_res_MHz, 'step between first and second element in axis')

    primary_hdu.header.set('OBS_LAT', f'{fits_config.get("OBS_LAT")}', 'observatory latitude in degree')
    primary_hdu.header.set('OBS_LAC', 'N', 'observatory latitude code {N,S}')
    primary_hdu.header.set('OBS_LON', f'{fits_config.get("OBS_LON")}', 'observatory longitude in degree')
    primary_hdu.header.set('OBS_LOC', 'W', 'observatory longitude code {E,W}')
    primary_hdu.header.set('OBS_ALT', f'{fits_config.get("OBS_ALT")}', 'observatory altitude in meter asl')


    # Wrap arrays in an additional dimension to mimic the e-CALLISTO storage
    time_array_wrapped = np.array([S.time_seconds.astype(np.float64)])
    freqs_MHz_wrapped = np.array([S.freq_MHz.astype(np.float64)])
    
    # Binary Table HDU (extension)
    col1 = fits.Column(name='TIME', format='PD', array=time_array_wrapped)
    col2 = fits.Column(name='FREQUENCY', format='PD', array=freqs_MHz_wrapped)
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
    hdul.writeto(path_to_fits, overwrite=True)


