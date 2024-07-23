# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import OrderedDict
import os
import warnings
from datetime import datetime
from typing import Tuple

from spectre.chunks.factory import get_chunk_from_tag
from spectre.chunks.BaseChunk import BaseChunk
from spectre.utils import dir_helpers, datetime_helpers
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.spectrogram import factory
from cfg import CONFIG

class Chunks:
    def __init__(self, 
                 tag: str, 
                 year=None, 
                 month=None, 
                 day=None):
        self.tag = tag
        
        # if a specific date is specified via kwargs, set the attribute
        # for chunks dir with the date dir appended.
        self.chunks_dir = CONFIG.path_to_chunks_dir
        if (not year is None) or (not month is None) or (not day is None):
            # if the user specifies any of the date kwargs, call that method to append to the parent chunks directory
            self.chunks_dir = datetime_helpers.append_date_dir(CONFIG.path_to_chunks_dir, 
                                                               year=year, 
                                                               month=month, 
                                                               day=day)

        self.Chunk = get_chunk_from_tag(tag)
        self._set_chunk_map()


    def _set_chunk_map(self) -> None:
        chunk_map = OrderedDict()

        ext_chunk_files = dir_helpers.list_all_files(self.chunks_dir)
        
        if len(ext_chunk_files) == 0:
            raise FileNotFoundError(f"No chunks found at {self.chunks_dir}.")
        
        for ext_chunk_file in ext_chunk_files:
            file_name, _ = os.path.splitext(ext_chunk_file)
            try:
                chunk_start_time, tag = file_name.split("_", 1)
            except ValueError as e:
                print(f"Error while splitting {file_name} at \"_\". Received {e}")
            # only consider chunks with the specified tag
            if tag == self.tag:
                chunk_map[chunk_start_time] = self.Chunk(chunk_start_time, tag)
        
        # sort the dictionary by keys in ascending chronological order
        chunk_map = OrderedDict(sorted(chunk_map.items()))
        
        # finally, set the attribute
        self.chunk_map = chunk_map
        return


    def get_chunk_start_time_list(self):
        return list(self.chunk_map.keys()) 
    

    def get_chunk_list(self):
        return list(self.chunk_map.values())
    

    def get_chunk_by_chunk_start_time(self, chunk_start_time: str) -> BaseChunk:
        chunk = self.chunk_map.get(chunk_start_time)
        if chunk is None:
            raise KeyError(f"Chunk with chunk start time {chunk_start_time} could not be found within {self.chunks_dir}")
        return chunk


    def get_chunk_by_item_index(self, item_index: int) -> BaseChunk:
            num_chunks = len(self.chunk_map) 
            index = index % num_chunks  # Use modulo to make the index wrap around. Allows the user to iterate over all the chunks via index cyclically.
            
            chunk_list = self.get_chunk_list()
            for i, chunk in enumerate(chunk_list):
                if i == item_index:
                    return chunk
        
            # Return Although logically this part should never be reached because of the modulo operation
            warnings.warn(f"Unexpected error! Index {index} out of bounds for maximum index {num_chunks-1}.", RuntimeWarning)
            return None


    def get_item_index_by_chunk(self, chunk_to_match: BaseChunk) -> int:
        chunk_list = self.get_chunk_list()
        for i, chunk in enumerate(chunk_list):
            if chunk.chunk_start_time == chunk_to_match.chunk_start_time:
                return i
        raise ValueError(f"No matching chunk found with chunk_start_time {chunk_to_match.chunk_start_time}.")
    


    def build_spectrogram_from_range(self, start_time_str: str, end_time_str: str) -> Spectrogram:
        start_time = datetime.strptime(start_time_str, CONFIG.default_time_format)
        end_time = datetime.strptime(end_time_str, CONFIG.default_time_format)

        if start_time.day != end_time.day:
            warnings.warn("Warning! Joining spectrograms over more than one day.", RuntimeWarning)

        target_day = start_time.day
        chunk_intervals = self.get_upper_bound_chunk_intervals()
        spectrograms = []

        for chunk_start_time, chunk in self.chunk_map.items():
            if chunk.chunk_start_datetime.day != target_day or not chunk.fits.exists():
                continue

            lower_bound, upper_bound = chunk_intervals[chunk_start_time]

            if lower_bound < end_time and upper_bound > start_time:
                spectrogram = chunk.fits.read()
                chopped_spectrogram = factory.time_chop(spectrogram, start_time_str, end_time_str)
                if chopped_spectrogram is None:
                    raise ValueError("Error chopping spectrogram within the specified time range.")
                spectrograms.append(chopped_spectrogram)

        return factory.join_spectrograms(spectrograms)

    

    def get_upper_bound_chunk_intervals(self) -> dict[str, Tuple[datetime, datetime]]:
        chunk_list = self.get_chunk_list()
        total_chunks = len(chunk_list)
        chunk_intervals = {}

        for i, chunk in enumerate(chunk_list):
            if not chunk.fits.exists():
                continue

            start_time = chunk.chunk_start_datetime
            end_time = chunk_list[i + 1].chunk_start_datetime if i < total_chunks - 1 else chunk.fits.get_datetimes()[-1]

            chunk_intervals[chunk.chunk_start_time] = (start_time, end_time)

        return chunk_intervals

