# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import OrderedDict
import os
import warnings
from datetime import datetime
from typing import Tuple, Iterator

from spectre.chunks.factory import get_chunk_from_tag
from spectre.chunks.BaseChunk import BaseChunk
from spectre.utils import dir_helpers, datetime_helpers
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.spectrogram import transform

from cfg import (
    CHUNKS_DIR_PATH,
    DEFAULT_TIME_FORMAT
)

class Chunks:
    def __init__(self, 
                 tag: str, 
                 year: int = None, 
                 month: int = None, 
                 day: int = None):
        self.tag = tag
        
        # set the directory which holds the chunks (by default, we use the entire chunks directory)
        self.chunks_dir = CHUNKS_DIR_PATH
        # if the user specifies any of the date kwargs, call that method to append to the parent chunks directory
        if (year is not None) or (month is not None) or (day is not None):
            self.chunks_dir = datetime_helpers.append_date_dir(CHUNKS_DIR_PATH, 
                                                               year=year, 
                                                               month=month, 
                                                               day=day)

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
        ext_chunk_files = dir_helpers.list_all_files(self.chunks_dir)
        
        # if there are no files at all
        if len(ext_chunk_files) == 0:
            warnings.warn("No chunks found, setting chunk map with empty dictionary.")
            # set with an empty dictionary
            self.chunk_map = chunk_map
            # and proceed no further
            return
        
        # for each chunk extension file
        for ext_chunk_file in ext_chunk_files:
            # split the extension from the file name
            file_name, _ = os.path.splitext(ext_chunk_file)
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
            raise KeyError(f"Chunk with chunk start time {chunk_start_time} could not be found within {self.chunks_dir}")
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


    def build_spectrogram_from_range(self, start_time_str: str, end_time_str: str) -> Spectrogram:
        start_time = datetime.strptime(start_time_str, DEFAULT_TIME_FORMAT)
        end_time = datetime.strptime(end_time_str, DEFAULT_TIME_FORMAT)

        if start_time.day != end_time.day:
            warnings.warn("Warning! Joining spectrograms over more than one day.", RuntimeWarning)

        target_day = start_time.day
        chunk_intervals = self.get_upper_bound_chunk_intervals()
        spectrograms = []

        for chunk_start_time, chunk in self.chunk_map.items():
            if chunk.chunk_start_datetime.day != target_day or not chunk.has_file("fits"):
                continue

            lower_bound, upper_bound = chunk_intervals[chunk_start_time]

            if lower_bound < end_time and upper_bound > start_time:
                spectrogram = chunk.fits.read()
                chopped_spectrogram = transform.time_chop(spectrogram, start_time_str, end_time_str)
                if chopped_spectrogram is None:
                    raise ValueError("Error chopping spectrogram within the specified time range.")
                spectrograms.append(chopped_spectrogram)

        return transform.join_spectrograms(spectrograms)


    def get_upper_bound_chunk_intervals(self) -> dict[str, Tuple[datetime, datetime]]:
        chunk_list = self.get_chunk_list()
        total_chunks = len(chunk_list)
        chunk_intervals = {}

        for i, chunk in enumerate(chunk_list):
            if not chunk.has_file("fits"):
                continue

            start_time = chunk.chunk_start_datetime
            end_time = chunk_list[i + 1].chunk_start_datetime if i < total_chunks - 1 else chunk.fits.get_datetimes()[-1]

            chunk_intervals[chunk.chunk_start_time] = (start_time, end_time)

        return chunk_intervals
