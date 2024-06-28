# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from typing import Tuple

from spectre.chunks.ChunkExt import ChunkExt


class ChunkBin(ChunkExt):
    def __init__(self, chunk_start_time: str, tag: str):
        super().__init__(chunk_start_time, tag, ".bin")

    def read(self) -> Tuple[int, np.ndarray]:
        try:
            with open(self.get_path(), "rb") as fh:
                # As per the functionality of batched file sink block
                # we store the ms correction correction at the start of the byte stream
                # as a 32 bit integer. We first extract this ...
                millisecond_correction = np.fromfile(fh, dtype=np.int32, count=1)[0]
                # Then read the remaining data as float32 and reshape it into vectors of length 3
                frequency_tagged_IQ_data = np.fromfile(fh, dtype=np.float32).reshape(-1, 3)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error fetching vector data, received {e}.")
        return (millisecond_correction,frequency_tagged_IQ_data)