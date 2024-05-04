from datetime import datetime, timedelta
import os
import numpy as np

from cfg import CONFIG


def date_dir(dt: datetime, **kwargs) -> str:
    # Format the datetime object to the desired string format
    year, month, day = dt.strftime("%Y"), dt.strftime("%m"), dt.strftime("%d")
    date_dir = os.path.join(year, month, day)
    # Format the datetime object to the desired string format
    base_dir = kwargs.get('base_dir', None)
    if base_dir:
        return os.path.join(base_dir, date_dir)
    else:
        return date_dir
    
    
def append_date_dir(parent_dir: str, **kwargs):
    # if the year, year month, or year month and day is specified, build the
    year = kwargs.get("year")
    month = kwargs.get("month")
    day = kwargs.get("day")

    if year is None and month is None and day is None:
        return parent_dir

    # Validate the combinations of year, month, and day
    if day and not month:
        raise ValueError("Day specified without month.")
    if (month or day) and not year:
        raise ValueError("Month or day specified without year.")
    if day and not (year and month):
        raise ValueError("Day specified without both year and month.")
    
    if year:
        dt = datetime(year=year, month=1, day=1)
        parent_dir = os.path.join(parent_dir, dt.strftime("%Y"))
    if year and month:
        dt = datetime(year=year, month=month, day=1)
        parent_dir = os.path.join(parent_dir, dt.strftime("%m"))
    if year and month and day:
        dt = datetime(year=year, month=month, day=day)
        parent_dir = os.path.join(parent_dir, dt.strftime("%d"))
    
    return parent_dir


def build_chunks_dir(chunk_start_time: str) -> str:
    # Parse the datetime string to a datetime object
    try:
        dt = datetime.strptime(chunk_start_time, CONFIG.default_time_format)
    except ValueError as e:
        raise ValueError(f"Could not parse {chunk_start_time}, received {e}.")
    return date_dir(dt, base_dir=CONFIG.chunks_dir)


def build_datetime_array(start_datetime: datetime, time_seconds: np.ndarray) -> list:
    # Validate input types      
    if not isinstance(start_datetime, datetime):
        raise TypeError("start_datetime must be a datetime object")
    if not isinstance(time_seconds, (np.ndarray, list, tuple)):
        raise TypeError("time_seconds must be an array, list, or tuple of numbers")

    try:    
        return [start_datetime + timedelta(seconds=ts) for ts in time_seconds]
    except ValueError:
        raise ValueError("time_seconds must only contain numeric values")


def transform_time_format(input_string: str, original_format: str, transformed_format: str) -> str:
    try:
        # Directly parse and return the formatted datetime string
        return datetime.strptime(input_string, original_format).strftime(transformed_format)
    except ValueError as e:
        raise ValueError(f"Error parsing '{input_string}' with format '{original_format}': {e}")
    


def seconds_of_day(dt: datetime) -> float:
    # Validate input type
    if not isinstance(dt, datetime):
        raise TypeError("dt must be a datetime object")
    
    start_of_day = datetime(dt.year, dt.month, dt.day)
    return (dt - start_of_day).total_seconds()


def find_closest_index(val: datetime, ar: np.ndarray) -> int:
    # Convert Python datetime to numpy datetime64 if necessary
    if isinstance(val, datetime):
        val = np.datetime64(val)
    if isinstance(ar, (list, tuple, np.ndarray)):
        ar = np.array(ar, dtype='datetime64[ns]')  # Convert list or tuple to numpy array of datetime64
    elif isinstance(ar, np.ndarray) and not np.issubdtype(ar.dtype, np.datetime64):
        ar = ar.astype('datetime64[ns]')  # Convert existing numpy array elements to datetime64
    
    # Validate data types
    if not np.issubdtype(ar.dtype, np.datetime64) or not isinstance(val, np.datetime64):
        raise TypeError("Both 'val' and elements of 'ar' must be datetime64 compatible types.")

    # Calculate absolute differences in nanoseconds and find the index of the minimum
    closest_index = np.argmin(np.abs(ar - val))
    return closest_index


def seconds_elapsed(datetimes: np.ndarray) -> np.ndarray:
    if not isinstance(datetimes, np.ndarray):
        raise TypeError(f"Input must be of type list. Received type {type(datetimes).__name__} instead.")
    
    if datetimes is None:
        raise ValueError("The input list is empty. Please provide a list with at least one datetime object.")

    if not all(isinstance(dt, datetime) for dt in datetimes):
        raise TypeError("All elements of the list must be datetime objects.")

    # Extract the first datetime to use as the reference point
    base_time = datetimes[0]
    

    # Calculate elapsed time in seconds for each datetime in the list
    elapsed_seconds = [(dt - base_time).total_seconds() for dt in datetimes]

    # Convert the list of seconds to a NumPy array of type float64
    return np.array(elapsed_seconds, dtype=np.float64)
