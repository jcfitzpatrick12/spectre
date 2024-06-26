# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime
from cfg import CONFIG
from spectre.utils import datetime_helpers

class BaseChunk:
    def __init__(self, chunk_start_time: str, tag: str):
        self.chunk_start_time = chunk_start_time
        self.tag = tag
        try:
            self.chunk_start_datetime = datetime.strptime(self.chunk_start_time, CONFIG.default_time_format)
        except ValueError as e:
            raise ValueError(f"Could not parse {chunk_start_time}, received {e}.")
        
        self.chunk_dir = datetime_helpers.build_chunks_dir(self.chunk_start_time)
        self.chunk_start_datetime = datetime.strptime(chunk_start_time, CONFIG.default_time_format)