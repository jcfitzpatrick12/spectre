from collections import OrderedDict
import os
import warnings
from datetime import datetime
from typing import Tuple

from spectre.chunks.get_chunk import get_chunk_from_tag
from spectre.utils import dir_helpers, datetime_helpers
from cfg import CONFIG
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.spectrogram import factory

class Chunks:
    def __init__(self, tag: str, chunks_dir: str, json_configs_dir: str, **kwargs):
        self.tag = tag
        self.chunks_dir = chunks_dir
        self.json_configs_dir = json_configs_dir
        
        # if a specific date is specified via kwargs, set the attribute
        # for chunks dir with the date dir appended.
        self.chunks_dir_with_time_dir = None
        year = kwargs.get("year")
        month = kwargs.get("month")
        day = kwargs.get("day")
        if (not year is None) or (not month is None) or (not day is None):
            # if the user specifies any of the date kwargs, call that method to append to the parent chunks directory
            self.chunks_dir_with_time_dir = datetime_helpers.append_date_dir(self.chunks_dir, **kwargs)

        self.Chunk = get_chunk_from_tag(tag, json_configs_dir)
        self.dict = self.build_dict()


    def build_dict(self) -> None:
        chunks_dict = OrderedDict()

        # if the user has specified a certain day, consider only files in that directory
        if self.chunks_dir_with_time_dir:
            files = dir_helpers.list_all_files(self.chunks_dir_with_time_dir)
        # otherwise consider all chunks in the chunks directory
        else:
            files = dir_helpers.list_all_files(self.chunks_dir)

        for file in files:
            file_name, ext = os.path.splitext(file)
            try:
                chunk_start_time, tag = file_name.split("_", 1)
            except ValueError as e:
                print(f"Error while splitting {file_name} at \"_\". Received {e}")
            # only consider chunks with the specified tag
            if tag == self.tag:
                chunks_dict[chunk_start_time] = self.Chunk(chunk_start_time, tag, self.chunks_dir, self.json_configs_dir)
        
        # sort the dictionary and set the attribute
        return OrderedDict(sorted(chunks_dict.items()))


    def get_chunk_by_index(self, index: int):
            if not self.dict:  # Check if the dictionary is empty
                print("The chunk dictionary is empty. Returning None.")
                return None

            # Normalize index to be within the bounds using modulo
            num_chunks = len(self.dict)  # Number of items in the dictionary
            index = index % num_chunks  # Use modulo to make the index wrap around

            for i, chunk in enumerate(self.dict.values()):
                if i == index:
                    return chunk
            
            # Although logically this part should never be reached because of the modulo operation
            warnings.warn(f"Unexpected error! Index {index} out of bounds for maximum index {num_chunks-1}.", RuntimeWarning)
            return None


    def get_index_by_chunk(self, chunk_to_match) -> int:
        chunk_start_time_to_match = chunk_to_match.chunk_start_time

        for index, chunk in enumerate(self.dict.values()):
            if chunk.chunk_start_time == chunk_start_time_to_match:
                return index

        raise ValueError(f"No matching chunk found with chunk_start_time {chunk_start_time_to_match}.")
    

    def find_nearest_chunk(self, requested_chunk_start_time: str):
        try:
            requested_chunk_start_time = datetime.strptime(requested_chunk_start_time, CONFIG.default_time_format)
        except ValueError as e:
            raise ValueError(f"Invalid date format for current chunk. Expected {CONFIG.default_time_format}, but got {requested_chunk_start_time}.")
        
        closest_chunk = None
        min_time_diff = None

        for chunk in self.dict.values():
            # extract the chunk_start_time for the current chunk 
            chunk_start_time = chunk.chunk_start_time
            
            # Calculate the absolute time difference
            time_diff = abs(requested_chunk_start_time - chunk_start_time)

            # Determine if this is the closest chunk so far
            if (min_time_diff is None) or (time_diff < min_time_diff):
                closest_chunk = chunk
                min_time_diff = time_diff

        if closest_chunk is None:
            raise ValueError(f"Unexpected error, closest chunk could not be evaluated. Found {closest_chunk}.")

        return closest_chunk
    

    def build_spectrogram_from_range(self, requested_start_str: str, requested_end_str: str) -> Spectrogram:
        requested_start_datetime = datetime.strptime(requested_start_str, CONFIG.default_time_format)
        requested_end_datetime = datetime.strptime(requested_end_str, CONFIG.default_time_format)


        if requested_start_datetime.day != requested_end_datetime.day:
            warnings.warn(f"Warning! Joining spectrograms over a time interval of more than one day.", RuntimeWarning)

        # can now safely set the day requested
        requested_day = requested_start_datetime.day

        # get the upper bound chunk intervals map
        upper_bound_chunk_intervals = self.get_upper_bound_chunk_intervals()

        spectrogram_list = []
        for chunk_start_time, chunk in self.dict.items():
            # if the current chunk does not match the requested datetime, just continue
            if chunk.chunk_start_datetime.day!=requested_day or not chunk.fits.exists():
                continue
            

            lower_bound_datetime = upper_bound_chunk_intervals[chunk_start_time][0]
            upper_bound_datetime = upper_bound_chunk_intervals[chunk_start_time][1]

            if lower_bound_datetime < requested_end_datetime and upper_bound_datetime > requested_start_datetime:
                S = chunk.fits.load_spectrogram()
                S = factory.time_chop(S, requested_start_str, requested_end_str)
                if S is None:
                    raise ValueError(f"Could not time chop spectrogram while building from range.")
                spectrogram_list.append(S)

        return factory.join_spectrograms(spectrogram_list)
    

    def get_upper_bound_chunk_intervals(self) -> dict[str, Tuple[datetime, datetime]]: 

        chunk_list = list(self.dict.values())
        num_chunks = len(chunk_list)

         # # get the upper bound chunk intervals as a map s.t.
        # # chunk_start_time -> tuple[t0, t1]
        # where t0 is the current chunk start time as a datetime
        # and t1 is the upper bound on the chunk end time as a datetime
        # which we define to be the start of the next chunk
        upper_bound_chunk_intervals = {}

        for i, chunk in enumerate(chunk_list):
            if not chunk.fits.exists():
                continue
            
            t0 = chunk.chunk_start_datetime

            if i < num_chunks - 1:
                next_chunk = chunk_list[i+1]
                t1 = next_chunk.chunk_start_datetime
            
            # if we are at the last chunk, just explicately evaluate it
            else:
                datetimes = chunk.fits.get_datetimes()
                t1 = datetimes[-1]
            
            upper_bound_chunk_intervals[chunk.chunk_start_time] = (t0, t1)
        
        return upper_bound_chunk_intervals
