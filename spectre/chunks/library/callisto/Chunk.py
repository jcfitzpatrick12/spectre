# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.chunks.BaseChunk import BaseChunk
from spectre.chunks.chunk_register import register_chunk
from spectre.chunks.library.callisto.FitsChunk import FitsChunk


@register_chunk('callisto')
class Chunk(BaseChunk):
    def __init__(self, chunk_start_time: str, tag: str):
        super().__init__(chunk_start_time, tag) 
        
        self.add_file(FitsChunk(chunk_start_time, tag))




