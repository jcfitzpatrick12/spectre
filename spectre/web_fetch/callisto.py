from datetime import datetime
import os
import subprocess
import shutil

from spectre.utils import callisto_helpers
from cfg import CONFIG

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
def wget_callisto_station(station: str, year: int, month: int, day: int):

    temp_datetime = datetime(year=year, month=month, day=day)
    formatted_year = temp_datetime.strftime("%Y")
    formatted_month = temp_datetime.strftime("%m")
    formatted_day = temp_datetime.strftime("%d")

    base_url = f"http://soleil.i4ds.ch/solarradio/data/2002-20yy_Callisto/{formatted_year}/{formatted_month}/{formatted_day}/"

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


def fetch_chunks(station: str, 
                 year=None, 
                 month=None, 
                 day=None):
    
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    # Validate the combinations of year, month, and day
    if day and not month:
        raise ValueError("Day specified without month.")
    if (month or day) and not year:
        raise ValueError("Month or day specified without year.")
    if day and not (year and month):
        raise ValueError("Day specified without both year and month.")
    
    wget_callisto_station(station, year, month, day)
    copy_to_chunks()

    shutil.rmtree(temp_dir)
    return