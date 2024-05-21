from datetime import datetime
import os
import subprocess
import shutil

from spectre.utils import callisto_helpers

temp_dir = os.path.join(os.environ['SPECTREPARENTPATH'], "tmp")

def copy_to_chunks():
    # Iterate through all files in the specified directory
    for entry in os.scandir(temp_dir):
        if entry.is_file() and entry.name.endswith('.gz'):
            gz_path = entry.path
            # Define a new output path for the uncompressed file
            callisto_helpers.unzip_to_chunks_dir(gz_path) # unzip 
            os.remove(gz_path)
            

# fetches all .fits.gz files and saves them inside fpath for a particular date and callisto station
def wget_callisto_station(station: str, date_as_string: str):

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
        '-R', '.tmp', # reject all .tmp file 
        '-A', f'{station}*.fit.gz', # download all .fit.gz for the appropriate station
        '-P', f'{temp_dir}', # download the files into the temp directory
        f"{base_url}" 
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


def fetch_chunks(station: str, date_as_string: str):
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    wget_callisto_station(station, date_as_string)
    copy_to_chunks()

    shutil.rmtree(temp_dir)
    return