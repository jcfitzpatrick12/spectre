# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

import os

from spectre.spectrograms.spectrogram import Spectrogram
from spectre.watchdog.base import BaseEventHandler
from spectre.watchdog.event_handler_register import register_event_handler

@register_event_handler("sweep")
class EventHandler(BaseEventHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.previous_chunk = None # cache for previous chunk
        

    def process(self, file_path: str):
        _LOGGER.info(f"Processing: {file_path}")
        file_name = os.path.basename(file_path)
        chunk_start_time, _ = os.path.splitext(file_name)[0].split('_')
        chunk = self._Chunk(chunk_start_time, self._tag)

        _LOGGER.info("Creating spectrogram")
        spectrogram = chunk.build_spectrogram(previous_chunk = self.previous_chunk)

        _LOGGER.info("Averaging spectrogram")
        spectrogram = self.average_in_time(spectrogram)
        spectrogram = self.average_in_frequency(spectrogram)

        _LOGGER.info("Joining spectrogram")
        self.join_spectrogram(spectrogram)

        # if the previous chunk has not yet been set, it means we were processing the first chunk
        # so we don't need to handle the previous chunk
        if self.previous_chunk is None:
            # instead, only set it for the next time this method is called
            self.previous_chunk = chunk
            
        # otherwise the previous chunk is defined (and by this point has already been processed)
        else:
            bin_chunk = self.previous_chunk.get_file('bin')
            _LOGGER.info(f"Deleting {bin_chunk.file_path}")
            bin_chunk.delete(doublecheck_delete = False)

            hdr_chunk = self.previous_chunk.get_file('hdr')
            _LOGGER.info(f"Deleting {hdr_chunk.file_path}")
            hdr_chunk.delete(doublecheck_delete = False)

            # and reassign the current chunk to be used as the previous chunk at the next call of this method
            self.previous_chunk = chunk
