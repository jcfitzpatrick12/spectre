# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import time
from watchdog.events import FileSystemEventHandler
from abc import ABC, abstractmethod

from spectre.chunks.get_chunk import get_chunk_from_tag
from spectre.json_config.CaptureConfigHandler import CaptureConfigHandler

class BaseEventHandler(FileSystemEventHandler, ABC):
    def __init__(self, watcher, tag: str, extension: str):
        self.watcher = watcher  # Pass the watcher instance to handle stopping events gracefully
        self.tag = tag
        self.Chunk = get_chunk_from_tag(tag)
        capture_config_handler = CaptureConfigHandler(tag)
        self.capture_config = capture_config_handler.load_as_dict()
        self.extension = extension


    @abstractmethod
    def process(self, file_path: str) -> None:
        pass


    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(self.extension):
            self.wait_until_stable(event.src_path)
            try:
                self.process(event.src_path)
            except Exception as e:
                print(f"Error processing file {event.src_path}: {e}")
                self.watcher.stop()  # Signal the watcher to stop on error


    def wait_until_stable(self, file_path: str):
        print(f"Waiting until {file_path} is stable.")
        size = -1
        while True:
            try:
                current_size = os.path.getsize(file_path)
                if current_size == size:
                    break
                size = current_size
                time.sleep(0.5)
            except OSError as e:
                print(f"Error accessing file {file_path}: {e}")
                self.watcher.stop()  # Stop if there's an error accessing the file
                break
        print(f"File {file_path} is stable and ready for processing.")

