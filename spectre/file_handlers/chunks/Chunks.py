# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import OrderedDict
from os import walk
from os.path import splitext
import warnings
from datetime import datetime, timedelta
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
        for chunk_file in chunk_files:
            # split the extension from the file name
            file_name, _ = splitext(chunk_file)
            # then from the file name split the chunk start time from the tag
            chunk_start_time, tag = file_name.split("_", 1)
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
    def get_chunk_start_time_list(self) -> list[str]:
        return list(self.chunk_map.keys()) 


    # getter for the list of chunks (already sorted chronologically)
    def get_chunk_list(self) -> list[BaseChunk]:
        return list(self.chunk_map.values())


    # get chunk by the chunk start time
    def get_chunk_by_chunk_start_time(self, chunk_start_time: str) -> BaseChunk:
        chunk = self.chunk_map.get(chunk_start_time)
        if chunk is None:
            raise KeyError(f"Chunk with chunk start time {chunk_start_time} could not be found within {self.chunks_dir_path}")
        return chunk


    # get chunk by the index
    def get_chunk_by_index(self, chunk_index: int) -> BaseChunk:
        # find the number of chunks
        num_chunks = len(self.chunk_map) 
        index = chunk_index % num_chunks  # Use modulo to make the index wrap around. Allows the user to iterate over all the chunks via index cyclically.
        return self._chunk_list[index]


    def get_index_by_chunk(self, chunk_to_match: BaseChunk) -> int:
        for i, chunk in enumerate(self):
            if chunk.chunk_start_time == chunk_to_match.chunk_start_time:
                return i
        raise ValueError(f"No matching chunk found with chunk_start_time {chunk_to_match.chunk_start_time}.")
    
    def count_chunk_files(self, extension: str) -> int:
        return sum(1 for chunk_file in self if chunk_file.has_file(extension))


    def get_spectrogram_from_range(self, start_time: str, end_time: str) -> Spectrogram:
        # Convert input strings to datetime objects
        start_datetime = datetime.strptime(start_time, DEFAULT_TIME_FORMAT)
        end_datetime = datetime.strptime(end_time, DEFAULT_TIME_FORMAT)

        if start_datetime.day != end_datetime.day:
            warnings.warn("Joining spectrograms across multiple days.", RuntimeWarning)

        # List to store spectrograms, which we will later stitch together
        spectrograms = []
        # evaluate the total number of fits files
        num_fits_chunks = self.count_chunk_files("fits")
        # Iterate through each chunk's start time and spectrogram data
        for i, chunk in enumerate(self):
            # skip chunks without fits files
            if not chunk.has_file("fits"):
                continue
            
            # rather than reading all files to evaluate the actual upper bound to their time range (slow)
            # place an upper bound by using the chunk start datetime for the next chunk
            # this assumes that the chunks are non-overlapping (reasonable assumption)
            lower_bound = chunk.chunk_start_datetime
            if i < num_fits_chunks:
                next_chunk = self.get_chunk_by_index(i + 1)
                upper_bound = next_chunk.chunk_start_datetime
            # if there is no "next chunk" then we do have to read the file
            else:
                fits_chunk = chunk.get_file("fits")
                datetimes = fits_chunk.get_datetimes()
                upper_bound = datetimes[-1]

            # if the chunk overlaps with the input time range, then read the fits file
            if start_datetime <= upper_bound and lower_bound <= end_datetime:
                # Read the spectrogram for this chunk
                spectrogram = chunk.read_file("fits")

                # Chop the spectrogram to fit within the requested time range
                spectrogram = transform.time_chop(spectrogram, start_time, end_time)
                
                # if we have a non-empty spectrogram, append it to the list of spectrograms
                if spectrogram:
                    # Add the chopped spectrogram to the list
                    spectrograms.append(spectrogram)

        # Join all the collected spectrograms into a single spectrogram
        if spectrograms:
            return transform.join_spectrograms(spectrograms)
        else:
            raise ValueError("No spectrogram data found for the given time range.")

