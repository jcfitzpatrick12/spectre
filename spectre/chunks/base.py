# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from datetime import datetime
from abc import abstractmethod
from typing import Any

from spectre.file_handlers.base import BaseFileHandler
from spectre.cfg import get_chunks_dir_path
from spectre.file_handlers.json.handlers import CaptureConfigHandler
from spectre.spectrograms.spectrogram import Spectrogram
from spectre.cfg import (
    DEFAULT_DATETIME_FORMAT
)
from spectre.exceptions import (
    ChunkFileNotFoundError
)

class ChunkFile(BaseFileHandler):
    def __init__(self, chunk_parent_path: str, chunk_name: str, extension: str):
        self.extension = extension
        self.chunk_start_time, self.tag = chunk_name.split("_")
        self.chunk_start_datetime = datetime.strptime(self.chunk_start_time, 
                                                      DEFAULT_DATETIME_FORMAT)
        super().__init__(chunk_parent_path, chunk_name, extension = extension)


class BaseChunk:
    def __init__(self, chunk_start_time: str, tag: str, **kwargs):
        self.chunk_start_time = chunk_start_time
        self.tag = tag
        self.chunk_files = {}
        self.chunk_start_datetime = datetime.strptime(self.chunk_start_time, 
                                                      DEFAULT_DATETIME_FORMAT)
        self.chunk_parent_path = get_chunks_dir_path(year = self.chunk_start_datetime.year,
                                                     month = self.chunk_start_datetime.month,
                                                     day = self.chunk_start_datetime.day)
        self.chunk_name = f"{self.chunk_start_time}_{self.tag}"


    def add_file(self, chunk_file: ChunkFile) -> None:
        self.chunk_files[chunk_file.extension] = chunk_file
        return
    

    def get_extensions(self) -> list[str]:
        return self.chunk_files.keys()


    def get_file(self, extension: str) -> ChunkFile:
        try:
            return self.chunk_files[extension]
        except KeyError:
            raise ChunkFileNotFoundError(f"No chunk file found with extension '{extension}'")


    def read_file(self, extension: str):
        chunk_file = self.get_file(extension)
        return chunk_file.read()


    def delete_file(self, extension: str, doublecheck_delete: bool = True):
        chunk_file = self.get_file(extension)
        try:
            chunk_file.delete(doublecheck_delete=doublecheck_delete)
        except FileNotFoundError as e:
            raise ChunkFileNotFoundError(str(e))


    def has_file(self, extension: str) -> bool:
        try:
            chunk_file = self.get_file(extension)
            return chunk_file.exists()
        except ChunkFileNotFoundError:
            return False


class SPECTREChunk(BaseChunk):
    def __init__(self, chunk_start_time: str, tag: str, **kwargs):
        super().__init__(chunk_start_time, tag, **kwargs)
        # each SPECTRE chunk will have an associated capture config (as it was generated by the program)
        capture_config_handler = CaptureConfigHandler(tag)
        self.capture_config = capture_config_handler.read()

    # additionally, we should be able to create a spectrogram based on the raw data
    @abstractmethod
    def build_spectrogram(self) -> Spectrogram:
        pass