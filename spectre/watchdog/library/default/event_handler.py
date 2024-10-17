# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

import os

from spectre.watchdog.base import BaseEventHandler
from spectre.watchdog.event_handler_register import register_event_handler

@register_event_handler("default")
class EventHandler(BaseEventHandler):
    def __init__(self, watcher, tag: str):
        super().__init__(watcher, tag, "bin")

    def process(self, file_path: str):
        _LOGGER.info(f"Processing {file_path}")
        file_name = os.path.basename(file_path)
        chunk_start_time, _ = os.path.splitext(file_name)[0].split('_')
        chunk = self.Chunk(chunk_start_time, self.tag)
        spectrogram = chunk.build_spectrogram()

        _LOGGER.info("Spectrogram successfully created. Averaging...")
        spectrogram = self.average_in_time(spectrogram)
        spectrogram = self.average_in_frequency(spectrogram)

        _LOGGER.info("Saving spectrogram to file...")
        spectrogram.save()

        _LOGGER.info(f"Deleting {self.previous_chunk.get_file("bin").file_path}")
        chunk.delete_file("bin", doublecheck_delete = False)

        _LOGGER.info(f"Deleting {self.previous_chunk.get_file("hdr").file_path}")
        chunk.delete_file("hdr", doublecheck_delete = False)
        return
