from datetime import datetime, timedelta
import os
import numpy as np

from spectre.cfg import CONFIG


def date_dir(dt: datetime, **kwargs) -> str:
    # Format the datetime object to the desired string format
    year, month, day = dt.strftime("/%Y"), dt.strftime("%m"), dt.strftime("%d")
    date_dir = os.path.join(year, month, day)
    # Format the datetime object to the desired string format
    base_dir = kwargs.get('base_dir', None)
    if base_dir:
        return os.path.join(base_dir, date_dir)
    else:
        return date_dir


def build_chunks_dir(chunk_start_time: str, chunks_dir: str) -> str:
    # Parse the datetime string to a datetime object
    try:
        dt = datetime.strptime(chunk_start_time, CONFIG.default_time_format)
    except ValueError as e:
        raise ValueError(f"Could not parse {chunk_start_time}, received {e}.")
    return date_dir(dt, base_dir=chunks_dir)


def build_datetime_array(start_datetime: datetime, time_seconds: np.array) -> list:
    # Validate input types
    if not isinstance(start_datetime, datetime):
        raise TypeError("start_datetime must be a datetime object")
    if not isinstance(time_seconds, (np.ndarray, list, tuple)):
        raise TypeError("time_seconds must be an array, list, or tuple of numbers")

    try:
        return [start_datetime + timedelta(seconds=int(ts)) for ts in time_seconds]
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