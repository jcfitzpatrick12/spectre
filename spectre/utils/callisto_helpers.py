# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime
import gzip
import shutil
import os

from cfg import CONFIG
from spectre.utils import datetime_helpers

def get_chunk_name(station: str, date: str, time: str, instrument_code: str):
    station_datetime_as_string = f"{date}T{time}"
    station_datetime_obj = datetime.strptime(station_datetime_as_string, '%Y%m%dT%H%M%S')
    chunk_start_time = station_datetime_obj.strftime(CONFIG.default_time_format)

    tag = f"callisto-{station.lower()}-{instrument_code}"
    chunk_name = f'{chunk_start_time}_{tag}.fits'
    return chunk_name


def get_chunk_components(gz_path: str):
    # get the file name from the path
    file = gz_path.split('/')[-1]
    
    if not ".fit.gz" in file:
        raise ValueError(f"Unexpected extension format with file {file}. Expected .fit.gz")
    
    # strip the compression extension
    file_name_no_ext = file.rstrip(".fit.gz")
    # Split the basename by underscores
    parts = file_name_no_ext.split('_')
    
    if len(parts) != 4:
        raise ValueError("Filename does not conform to the expected format of [station]_[date]_[time]_[instrument_code]")
    
    station = parts[0]
    date = parts[1]
    time = parts[2]
    instrument_code = parts[3]

    return station, date, time, instrument_code


def derive_fits_chunk_path(gz_path: str):
    station, date, time, instrument_code = get_chunk_components(gz_path)
    fits_chunk_name = get_chunk_name(station, date, time, instrument_code)
    chunk_start_time = fits_chunk_name.split('_')[0]
    chunk_parent_path = datetime_helpers.get_chunk_parent_path(chunk_start_time)
    return os.path.join(chunk_parent_path, fits_chunk_name)


def unzip_to_chunks_dir(gz_path: str):
    fits_path = derive_fits_chunk_path(gz_path)
    # open the compressed fits, and a new file to hold the unzipped fits
    with gzip.open(gz_path, 'rb') as f_in, open(fits_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)