from datetime import datetime
import os
import subprocess
import gzip
import shutil

from cfg import CONFIG
from spectre.utils import datetime_helpers

temp_dir = os.path.join(os.environ['SPECTREPARENTPATH'], "tmp")

def __get_chunk_name(station: str, date: str, time: str, instrument_code: str):
    station_datetime_as_string = f"{date}{time}"
    station_datetime_obj = datetime.strptime(station_datetime_as_string, '%Y%m%d%H%M%S')
    chunk_start_time = station_datetime_obj.strftime(CONFIG.default_time_format)

    tag = f"callisto-{station.lower()}-{instrument_code}"
    chunk_name = f'{chunk_start_time}_{tag}.fits'
    return chunk_name


def __get_chunk_components(gz_path: str):
    # get the file name from the path
    file = gz_path.split('/')[-1]
    file_name_dot_fit, _ = os.path.splitext(file) 
    file_name, _ = os.path.splitext(file_name_dot_fit)
    
    # Split the basename by underscores
    parts = file_name.split('_')
    
    if len(parts) != 4:
        raise ValueError("Filename does not conform to the expected format of [station]_[date]_[time]_[instrument_code]")
    
    station = parts[0]
    date = parts[1]
    time = parts[2]
    instrument_code = parts[3]

    return station, date, time, instrument_code


def __derive_fits_chunk_path(gz_path: str):
    station, date, time, instrument_code = __get_chunk_components(gz_path)
    fits_chunk_name = __get_chunk_name(station, date, time, instrument_code)
    chunk_start_time = fits_chunk_name.split('_')[0]
    chunks_dir = datetime_helpers.build_chunks_dir(chunk_start_time)
    return os.path.join(chunks_dir, fits_chunk_name)


def __unzip_to_chunks_dir(gz_path: str):
    fits_path = __derive_fits_chunk_path(gz_path)
    # open the compressed fits, and a new file to hold the unzipped fits
    with gzip.open(gz_path, 'rb') as f_in, open(fits_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


def __copy_to_chunks():
    # Iterate through all files in the specified directory
    for entry in os.scandir(temp_dir):
        if entry.is_file() and entry.name.endswith('.gz'):
            gz_path = entry.path
            # Define a new output path for the uncompressed file
            __unzip_to_chunks_dir(gz_path) # unzip 
            os.remove(gz_path)
            

# fetches all .fits.gz files and saves them inside fpath for a particular date and callisto station
def __wget_callisto_station(station: str, date_as_string: str):
    date_format = "%Y-%m-%d"
    try:
        fetch_from_datetime = datetime.strptime(date_as_string, date_format)
    except ValueError as e:
        raise ValueError(f"Expected date format is {date_format} but got {date_as_string}. Received the error: {e}.")
    year = fetch_from_datetime.strftime("%Y")
    month = fetch_from_datetime.strftime("%m")
    day = fetch_from_datetime.strftime("%d")
    base_url = f"http://soleil.i4ds.ch/solarradio/data/2002-20yy_Callisto/{year}/{month}/{day}/"

    # wget -r -l1 -H -t1 -nd -N -np -e robots=off -A 'GLASGOW*.fit.gz' http://soleil.i4ds.ch/solarradio/data/2002-20yy_Callisto/2024/05/20/
    command = [
        'wget', '-r', '-l1', '-nd', '-np',
        '-R', '.tmp',
        '-A', f'{station}*.fit.gz', 
        '-P', f'{temp_dir}',
        f"{base_url}"
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


def fetch_chunks(station: str, date_as_string: str):
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    __wget_callisto_station(station, date_as_string)
    __copy_to_chunks()

    os.rmdir(os.path.join(os.environ['SPECTREPARENTPATH'], "tmp"))
    return