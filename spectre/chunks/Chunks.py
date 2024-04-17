from collections import OrderedDict
import os
import warnings
from datetime import datetime

from spectre.chunks.get_chunk import get_chunk_from_tag
from spectre.utils import dir_helpers
from spectre.cfg import CONFIG
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.spectrogram import factory

class Chunks:
    def __init__(self, tag: str, chunks_dir: str, json_configs_dir: str):
        self.tag = tag
        self.chunks_dir = chunks_dir
        self.json_configs_dir = json_configs_dir

        self.Chunk = get_chunk_from_tag(tag, json_configs_dir)
        self.all_files = dir_helpers.list_all_files(chunks_dir)
        self.set_dict()


    def set_dict(self) -> None:
        self.dict = OrderedDict()
        for file in self.all_files:
            file_name, ext = os.path.splitext(file)
            try:
                chunk_start_time, tag = file_name.split("_", 1)
            except ValueError as e:
                print(f"Error while splitting {file_name} at \"_\". Received {e}")
            # only consider chunks with the specified tag
            if tag==self.tag:
                self.dict[chunk_start_time] = self.Chunk(chunk_start_time, tag, self.chunks_dir, self.json_configs_dir)
        self.sort_dict()


    def sort_dict(self) -> None:
        self.dict = OrderedDict(sorted(self.dict.items()))


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

        spectrogram_list = []
        for chunk in self.dict.values():
            # if the current chunk does not match the requested datetime, just continue
            if chunk.chunk_start_datetime.day!=requested_day or not chunk.fits.exists():
                continue
            
            # extract (only!) the datetimes from the fits file (too bulky loading every spectrogram!)
            datetimes = chunk.fits.get_datetimes()

            if datetimes[0] <= requested_end_datetime and datetimes[-1] >= requested_start_datetime:
                S = chunk.fits.load_spectrogram()
                S = factory.time_chop(S, requested_start_str, requested_end_str)
                if S is None:
                    raise ValueError(f"Could not time chop spectrogram while building from range.")
                spectrogram_list.append(S)

        return factory.join_spectrograms(spectrogram_list)