# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

import os
import time
import queue
from abc import ABC, abstractmethod
from math import floor
from watchdog.events import FileSystemEventHandler

from spectre.chunks.factory import get_chunk_from_tag
from spectre.file_handlers.json.handlers import CaptureConfigHandler
from spectre.spectrograms.spectrogram import Spectrogram
from spectre.spectrograms.transform import join_spectrograms
from spectre.spectrograms.transform import (
    time_average, 
    frequency_average
)


class BaseEventHandler(ABC, FileSystemEventHandler):
    def __init__(self, tag: str, exception_queue: queue.Queue, extension: str):
        self.tag = tag
        self.Chunk = get_chunk_from_tag(tag)
        capture_config_handler = CaptureConfigHandler(tag)
        self.capture_config = capture_config_handler.read()
        self.extension = extension
        self.exception_queue = exception_queue  # Queue to propagate exceptions


    @abstractmethod
    def process(self, file_path: str) -> None:
        pass


    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(self.extension):
            _LOGGER.info(f"Noticed: {event.src_path}")
            self.wait_until_stable(event.src_path)
            try:
                # Process the file once it's stable
                self.process(event.src_path)
            except Exception as e:
                _LOGGER.error(f"An error has occured while processing {event.src_path}",
                              exc_info=True)
                # Capture the exception and propagate it through the queue
                self.exception_queue.put(e)


    def wait_until_stable(self, file_path: str):
        _LOGGER.info(f"Waiting for file stability: {file_path}")
        size = -1
        while True:
            try:
                current_size = os.path.getsize(file_path)
                if current_size == size:
                    _LOGGER.info(f"File is now stable: {file_path}")
                    break  # File is stable when the size hasn't changed
                size = current_size
                time.sleep(0.5)
            except OSError as e:
                self.flush_spectrogram() # flush the internally stored spectrogram
                self.exception_queue.put(e)  # Capture the exception and propagate it
                raise e


    def average_in_time(self, spectrogram: Spectrogram) -> Spectrogram:
        requested_time_resolution = self.capture_config.get('time_resolution') # [s]
        if requested_time_resolution is None:
            raise KeyError(f"Time resolution has not been specified in the capture config!")
        average_over = floor(requested_time_resolution/spectrogram.time_resolution) if requested_time_resolution > spectrogram.time_resolution else 1
        return time_average(spectrogram, average_over)
    
    
    def average_in_frequency(self, spectrogram: Spectrogram) -> Spectrogram:
        frequency_resolution = self.capture_config.get('frequency_resolution') # [Hz]
        if frequency_resolution is None:
            raise KeyError(f"Frequency resolution has not been specified in the capture config!")
        average_over = floor(frequency_resolution/spectrogram.frequency_resolution) if frequency_resolution > spectrogram.frequency_resolution else 1
        return frequency_average(spectrogram, average_over)
    

    def join_spectrogram(self, spectrogram: Spectrogram) -> None:
        # if the spectrogram attribute is empty, define it
        if self.spectrogram is None:
            self.spectrogram = spectrogram
            return
        # otherwise, effectively append it  
        else:
            self.spectrogram = join_spectrograms([self.spectrogram, spectrogram])
            if self.spectrogram.time_range > self.capture_config.get("joining_time"):
                self.flush_spectrogram()
    

    def flush_spectrogram(self) -> None:
        _LOGGER.info("Flushing spectrogram to file")
        if self.spectrogram:
            self.spectrogram.save()
            _LOGGER.info("Flush successful, resetting state")
            self.spectrogram = None