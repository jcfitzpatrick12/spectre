# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import warnings
from math import floor

from spectre.watchdog.BaseEventHandler import BaseEventHandler
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.spectrogram import transform
from spectre.watchdog.event_handler_register import register_event_handler

@register_event_handler("sweep")
class EventHandler(BaseEventHandler):
    def __init__(self, watcher, tag: str):
        super().__init__(watcher, tag, "bin")

        # initialise an attribute which will store the previous chunk
        # this is required in order to avoid data dropping constructing swept spectrograms
        # when the sweep bleeds from one chunk into another
        self.previous_chunk = None # at instantiation, there is no previous chunk

    def process(self, file_path: str):
        print(f"Processing {file_path}")
        file_name = os.path.basename(file_path)
        chunk_start_time, _ = os.path.splitext(file_name)[0].split('_')
        chunk = self.Chunk(chunk_start_time, self.tag)
        S = chunk.build_spectrogram(previous_chunk = self.previous_chunk)
        average_over_int = self.get_average_over_int(S)
        S = transform.time_average(S, average_over_int)
        S.save_to_fits()
        print(f"Processing complete. Removing binary and header chunks with chunk start time: {chunk_start_time}.")

        # if the previous chunk has not yet been set, it means we were processing the first chunk
        # so we don't need to handle the previous chunk
        if self.previous_chunk is None:
            # instead, only set it for the next time this method is called
            self.previous_chunk = chunk
            
        # otherwise the previous chunk is defined (and by this point has already been processed)
        else:
            # delete the used binary and detached header files
            self.previous_chunk.bin.delete(doublecheck_delete = False)
            self.previous_chunk.hdr.delete(doublecheck_delete = False)
            # and reassign the current chunk to be used as the previous chunk at the next call of this method
            self.previous_chunk = chunk


    def get_average_over_int(self, S: Spectrogram) -> int:
        requested_integration_time = self.capture_config.get('integration_time')
        if requested_integration_time is None:
            raise KeyError(f"integration_time has not been specified in the capture config!")
    
        time_res_seconds = S.time_res_seconds

        if requested_integration_time <= S.time_res_seconds:
            warnings.warn(f'Requested integration time is lower than the time resolution of the spectrogram. No averaging taking place.')
            return 1
        
        return floor(requested_integration_time/time_res_seconds)
