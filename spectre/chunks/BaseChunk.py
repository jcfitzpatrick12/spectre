# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime
from abc import ABC

from spectre.utils import datetime_helpers
from spectre.file_handlers.BaseFileHandler import BaseFileHandler

from cfg import (
    DEFAULT_TIME_FORMAT
)

class BaseChunk(BaseFileHandler):
    def __init__(self, chunk_start_time: str, tag: str, **kwargs):
        self.chunk_start_time = chunk_start_time
        self.tag = tag

        self.chunk_start_datetime: datetime = datetime.strptime(self.chunk_start_time, 
                                                                DEFAULT_TIME_FORMAT)  
        
        parent_path = datetime_helpers.get_chunk_parent_path(self.chunk_start_time)  
        base_file_name = f"{chunk_start_time}_{tag}"
        super().__init__(parent_path, base_file_name, **kwargs) # no extension 

    
    def read(self, extension: str):
        if hasattr(self, extension):
            ext_chunk = getattr(self, extension)
            if callable(getattr(ext_chunk, 'read', None)):
                return ext_chunk.read()
            else:
                raise AttributeError(f"The attribute '{extension}' does not have a 'read' method.")
        else:
            raise AttributeError(f"The chunk named {self.chunk_name} does not have an attribute '{extension}'.")
