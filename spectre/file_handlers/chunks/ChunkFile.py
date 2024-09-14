# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from spectre.file_handlers.BaseFileHandler import BaseFileHandler
from spectre.utils.datetime_helpers import get_chunk_parent_path

class ChunkFile(BaseFileHandler):
    def __init__(self, chunk_parent_path: str, chunk_name: str, extension: str):
        self.extension = extension
        self.chunk_start_time, self.tag = chunk_name.split("_")
        super().__init__(chunk_parent_path, chunk_name, extension=self.extension)