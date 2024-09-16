# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import time
import queue
from watchdog.events import FileSystemEventHandler
from abc import ABC, abstractmethod

from spectre.file_handlers.chunks.factory import get_chunk_from_tag
from spectre.file_handlers.json.CaptureConfigHandler import CaptureConfigHandler


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
            self.wait_until_stable(event.src_path)
            try:
                # Process the file once it's stable
                self.process(event.src_path)
            except Exception as e:
                # Capture the exception and propagate it through the queue
                self.exception_queue.put(e)

    def wait_until_stable(self, file_path: str):
        size = -1
        while True:
            try:
                current_size = os.path.getsize(file_path)
                if current_size == size:
                    break  # File is stable when the size hasn't changed
                size = current_size
                time.sleep(0.5)
            except OSError as e:
                self.exception_queue.put(e)  # Capture the exception and propagate it
                raise e