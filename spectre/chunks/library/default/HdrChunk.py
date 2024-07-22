# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from typing import Tuple

from spectre.chunks.ExtChunk import ExtChunk

class HdrChunk(ExtChunk):
    def __init__(self, chunk_start_time: str, tag: str):
        super().__init__(chunk_start_time, tag, ".hdr")
    
    # TO BE IMPLEMENTED
    def read(self) -> int:
        return 0