# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime

from spectre.file_handlers.BaseFileHandler import BaseFileHandler
from cfg import (
    DEFAULT_TIME_FORMAT
)

class ChunkFile(BaseFileHandler):
    def __init__(self, chunk_parent_path: str, chunk_name: str, extension: str):
        self.extension = extension
        self.chunk_start_time, self.tag = chunk_name.split("_")
        self.chunk_start_datetime: datetime = datetime.strptime(self.chunk_start_time, 
                                                                DEFAULT_TIME_FORMAT)
        super().__init__(chunk_parent_path, chunk_name, extension=self.extension)