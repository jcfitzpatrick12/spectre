# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import subprocess
import shutil
import gzip
from datetime import datetime
from pathlib import Path

from cfg import CONFIG, callisto_stations
from spectre.utils import datetime_helpers

temp_dir = os.path.join(os.environ['SPECTREPARENTPATH'], "tmp")

def get_chunk_name(station: str, date: str, time: str, instrument_code: str) -> str:
    dt = datetime.strptime(f"{date}T{time}", '%Y%m%dT%H%M%S')
    formatted_time = dt.strftime(CONFIG.default_time_format)
    return f"{formatted_time}_callisto-{station.lower()}-{instrument_code}.fits"


def get_chunk_components(gz_path: str):
    file_name = os.path.basename(gz_path)
    if not file_name.endswith(".fit.gz"):
        raise ValueError(f"Unexpected file extension in {file_name}. Expected .fit.gz")
    
    file_base_name = file_name.rstrip(".fit.gz")
    parts = file_base_name.split('_')
    if len(parts) != 4:
        raise ValueError("Filename does not conform to the expected format of [station]_[date]_[time]_[instrument_code]")
    
    return parts


def get_chunk_path(gz_path: str) -> str:
    station, date, time, instrument_code = get_chunk_components(gz_path)
    fits_chunk_name = get_chunk_name(station, date, time, instrument_code)
    chunk_start_time = fits_chunk_name.split('_')[0]
    chunk_parent_path = datetime_helpers.get_chunk_parent_path(chunk_start_time)
    if not os.path.exists(chunk_parent_path):
        os.makedirs(chunk_parent_path)
    return os.path.join(chunk_parent_path, fits_chunk_name)


def unzip_file_to_chunks(gz_path: str):
    fits_path = get_chunk_path(gz_path)
    with gzip.open(gz_path, 'rb') as f_in, open(fits_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


def unzip_to_chunks():
    for entry in os.scandir(temp_dir):
        if entry.is_file() and entry.name.endswith('.gz'):
            unzip_file_to_chunks(entry.path)
            os.remove(entry.path)


def download_callisto_data(instrument_code: str, year: int, month: int, day: int):
    date_str = f"{year:04d}/{month:02d}/{day:02d}"
    base_url = f"http://soleil.i4ds.ch/solarradio/data/2002-20yy_Callisto/{date_str}/"
    command = [
        'wget', '-r', '-l1', '-nd', '-np', '-R', '.tmp',
        '-A', f'{instrument_code}*.fit.gz',
        '-P', temp_dir,
        base_url
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

def fetch_chunks(instrument_code: str, year: int, month: int, day: int):
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    if instrument_code not in callisto_stations.instrument_codes:
        raise ValueError(f"No match found for \"{instrument_code}\". Expected one of {callisto_stations.instrument_codes}")

    download_callisto_data(instrument_code, year, month, day)
    unzip_to_chunks()
    shutil.rmtree(temp_dir)
