# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import warnings
from math import floor

from spectre.watchdog.BaseEventHandler import BaseEventHandler
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.spectrogram import factory
from spectre.watchdog.event_handler_register import register_event_handler

@register_event_handler("default")
class EventHandler(BaseEventHandler):
    def __init__(self, watcher, tag: str):
        super().__init__(watcher, tag)

    def process(self, file_path: str):
        print(f"Processing {file_path}")
        file_name = os.path.basename(file_path)
        chunk_start_time, _ = os.path.splitext(file_name)[0].split('_')
        chunk = self.Chunk(chunk_start_time, self.tag)
        S = chunk.build_spectrogram()
        average_over_int = self.get_average_over_int(S)
        S = factory.time_average(S, average_over_int)
        S.save_to_fits()
        print(f"Processing complete. Removing {file_path}.")
        os.remove(file_path)


    def get_average_over_int(self, S: Spectrogram) -> int:
        requested_integration_time = self.capture_config.get('integration_time')
        if requested_integration_time is None:
            raise KeyError(f"integration_time has not been specified in the capture config!")
    
        time_res_seconds = S.time_res_seconds

        if requested_integration_time <= S.time_res_seconds:
            warnings.warn(f'Requested integration time is lower than the time resolution of the spectrogram. No averaging taking place.')
            return 1
        
        return floor(requested_integration_time/time_res_seconds)
