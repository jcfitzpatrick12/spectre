# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime

from spectre.file_handlers.chunks.ChunkFile import ChunkFile

from cfg import (
    DEFAULT_TIME_FORMAT
)
from cfg import get_chunks_dir_path


class BaseChunk:
    def __init__(self, chunk_start_time: str, tag: str, **kwargs):
        self.chunk_start_time = chunk_start_time
        self.tag = tag
        self.chunk_files = {}
        self.chunk_start_datetime = datetime.strptime(self.chunk_start_time, 
                                                      DEFAULT_TIME_FORMAT)
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
        if extension not in self.chunk_files:
            raise ValueError(f"No file registered with extension '{extension}'")
        return self.chunk_files[extension]


    def read_file(self, extension: str):
        chunk_file = self.get_file(extension)
        if chunk_file.exists():
            return chunk_file.read()
        else:
            raise FileNotFoundError(f"{chunk_file.file_path} was not found.")


    def delete_file(self, extension: str, doublecheck_delete: bool = True):
        chunk_file = self.get_file(extension)
        if chunk_file.exists():
            chunk_file.delete(doublecheck_delete=doublecheck_delete)
        else:
            raise FileNotFoundError(f"{chunk_file.file_path} was not found.")


    def has_file(self, extension: str) -> bool:
        chunk_file = self.chunk_files.get(extension)
        return chunk_file is not None and chunk_file.exists()

     
    
