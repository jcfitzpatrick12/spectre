# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from spectre.watchdog.base import BaseEventHandler
from spectre.watchdog.event_handler_register import register_event_handler

@register_event_handler("default")
class EventHandler(BaseEventHandler):
    def __init__(self, watcher, tag: str):
        super().__init__(watcher, tag, "bin")

    def process(self, file_path: str):
        file_name = os.path.basename(file_path)
        chunk_start_time, _ = os.path.splitext(file_name)[0].split('_')
        chunk = self.Chunk(chunk_start_time, self.tag)
        spectrogram = chunk.build_spectrogram()
        spectrogram = self.average_in_time(spectrogram)
        spectrogram = self.average_in_frequency(spectrogram)
        spectrogram.save()
        chunk.delete_file("bin", doublecheck_delete = False)
        chunk.delete_file("hdr", doublecheck_delete = False)
        return
