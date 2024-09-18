# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import OrderedDict
from os import walk
from os.path import splitext
import warnings
from datetime import datetime
from typing import Tuple, Iterator

from spectre.file_handlers.chunks.factory import get_chunk_from_tag
from spectre.file_handlers.chunks.BaseChunk import BaseChunk
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.spectrogram import transform

from cfg import (
    DEFAULT_TIME_FORMAT
)
from cfg import get_chunks_dir_path

class Chunks:
    def __init__(self, 
                 tag: str, 
                 year: int = None, 
                 month: int = None, 
                 day: int = None):
        self.tag = tag
        
        # set the directory which holds the chunks (by default, we use the entire chunks directory)
        self.chunks_dir_path = get_chunks_dir_path(year, month, day)

        # extract the appropriate chunk class based on the input tag
        self.Chunk = get_chunk_from_tag(tag)
        # set the chunk map
        self._set_chunk_map()

        # set some internal attributes which assist in making Chunks iterable
        self._chunk_list = self.get_chunk_list()
        self._current_index = 0

    # setter for chunk map
    def _set_chunk_map(self) -> None:
        # chunk map is an ordered dictionary, with each chunk ordered chronologically based on the chunk start time
        chunk_map = OrderedDict()
        # each file within chunks will be an extension instance of a chunk
        chunk_files = [f for (_, _, files) in walk(self.chunks_dir_path) for f in files]
        
        # if there are no files at all
        if len(chunk_files) == 0:
            warnings.warn("No chunks found, setting chunk map with empty dictionary.")
            # set with an empty dictionary
            self.chunk_map = chunk_map
            # and proceed no further
            return
        
        # for each chunk extension file
        for ext_chunk_file in chunk_files:
            # split the extension from the file name
            file_name, _ = splitext(ext_chunk_file)
            try:
                # then from the file name split the chunk start time from the tag
                chunk_start_time, tag = file_name.split("_", 1)
            except ValueError as e:
                raise ValueError(f"Error while splitting {file_name} at \"_\". Received {e}")
            # if the tag is equal to the user-defined tag, we will add that chunk to the chunk map
            if tag == self.tag:
                chunk_map[chunk_start_time] = self.Chunk(chunk_start_time, tag)
        
        # with all chunks accounted for, sort chronologically (as a precautionary measure) and set the populated chunk map
        self.chunk_map = OrderedDict(sorted(chunk_map.items()))

    # an alias for _set_chunk_map
    def update_chunk_map(self) -> None:
        self._set_chunk_map()
        return
    
    # enable iterative chunks
    def __iter__(self) -> Iterator[BaseChunk]:
        self._current_index = 0
        return self
    
    # enable iterative chunks
    # calling like an iterable will iterate over each chunk chronologically
    def __next__(self) -> BaseChunk:
        if self._current_index < len(self._chunk_list):
            chunk = self._chunk_list[self._current_index]
            self._current_index += 1
            return chunk
        else:
            raise StopIteration

    # getter for the list of chunk start times (already sorted chronologically)
    def get_chunk_start_time_list(self) -> list:
        return list(self.chunk_map.keys()) 

    # getter for the list of chunks (already sorted chronologically)
    def get_chunk_list(self) -> list:
        return list(self.chunk_map.values())

    # get chunk by the chunk start time
    def get_chunk_by_chunk_start_time(self, chunk_start_time: str) -> BaseChunk:
        chunk = self.chunk_map.get(chunk_start_time)
        if chunk is None:
            raise KeyError(f"Chunk with chunk start time {chunk_start_time} could not be found within {self.chunks_dir_path}")
        return chunk

    # get chunk by the index
    def get_chunk_by_index(self, item_index: int) -> BaseChunk:
        # find the number of chunks
        num_chunks = len(self.chunk_map) 
        index = item_index % num_chunks  # Use modulo to make the index wrap around. Allows the user to iterate over all the chunks via index cyclically.
        return self._chunk_list[index]


    def get_index_by_chunk(self, chunk_to_match: BaseChunk) -> int:
        for i, chunk in enumerate(self):
            if chunk.chunk_start_time == chunk_to_match.chunk_start_time:
                return i
        raise ValueError(f"No matching chunk found with chunk_start_time {chunk_to_match.chunk_start_time}.")


    def build_spectrogram_from_range(self, start_time: str, end_time: str) -> Spectrogram:
        # Convert input strings to datetime objects
        start_datetime = datetime.strptime(start_time, DEFAULT_TIME_FORMAT)
        end_datetime = datetime.strptime(end_time, DEFAULT_TIME_FORMAT)

        if start_datetime.day != end_datetime.day:
            warnings.warn("Joining spectrograms across multiple days.", RuntimeWarning)

        # Retrieve upper-bound intervals for all chunks
        chunk_intervals = self.get_upper_bound_chunk_intervals()

        # List to store spectrograms to join
        spectrograms = []

        # Iterate through each chunk's start time and spectrogram data
        for chunk_start_time, chunk in self.chunk_map.items():
            # Skip chunks without the correct file or if the day doesn't match
            if not chunk.has_file("fits"):
                continue

            # Get the time bounds for this chunk
            lower_bound, upper_bound = chunk_intervals.get(chunk_start_time, (None, None))
            
            # Ensure both lower and upper bounds are valid
            if lower_bound is None or upper_bound is None:
                continue
            
            # Check if the chunk time range overlaps the requested time range
            if lower_bound < end_datetime and upper_bound > start_datetime:
                # Read the spectrogram for this chunk
                spectrogram = chunk.read_file("fits")
                
                # Chop the spectrogram to fit within the requested time range
                chopped_spectrogram = transform.time_chop(spectrogram, start_time, end_time)
                
                # Add the chopped spectrogram to the list
                spectrograms.append(chopped_spectrogram)

        # Join all the collected spectrograms into a single spectrogram
        if spectrograms:
            return transform.join_spectrograms(spectrograms)
        else:
            raise ValueError("No spectrogram data found for the given time range.")



    def get_upper_bound_chunk_intervals(self) -> dict[str, Tuple[datetime, datetime]]:
        # Retrieve the list of chunks
        chunk_list = self.get_chunk_list()
        total_chunks = len(chunk_list)
        chunk_intervals = {}

        for i, chunk in enumerate(chunk_list):
            # Skip chunks without the required FITS file
            if not chunk.has_file("fits"):
                continue

            # Determine the start time of the current chunk
            start_time = chunk.chunk_start_datetime

            # Determine the end time based on the next chunk's start time or calculate the last chunk's end time
            if i < total_chunks - 1:
                # End time is the start time of the next chunk
                end_time = chunk_list[i + 1].chunk_start_datetime
            else:
                # For the last chunk, attempt to retrieve the exact end time from its own data
                end_times = chunk.get_file("fits").get_datetimes()
                if end_times:
                    end_time = end_times[-1]  # Use the last available time as the upper bound
                else:
                    # Use a fallback value if end times are unavailable
                    end_time = start_time + timedelta(hours=1)  # Adjust this as per data expectations

            # Store the start and end times for this chunk
            chunk_intervals[chunk.chunk_start_time] = (start_time, end_time)

        return chunk_intervals
