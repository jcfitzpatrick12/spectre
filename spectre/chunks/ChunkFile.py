# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from spectre.file_handlers.BaseFileHandler import BaseFileHandler
from spectre.utils.datetime_helpers import get_chunk_parent_path

class ChunkFile(BaseFileHandler):
    def __init__(self, chunk_start_time: str, tag: str, extension: str):
        self.chunk_start_time = chunk_start_time
        self.tag = tag
        self.extension = extension

        self.parent_path = get_chunk_parent_path(chunk_start_time)
        self.base_file_name = f"{self.chunk_start_time}_{tag}"
        super().__init__(self.parent_path, self.base_file_name, extension=self.extension)