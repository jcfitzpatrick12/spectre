# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np

from spectre.file_handlers.chunks.ChunkFile import ChunkFile

class BinChunk(ChunkFile):
    def __init__(self, chunk_parent_path: str, chunk_name: str):
        super().__init__(chunk_parent_path, chunk_name, "bin")

    def read(self) -> np.ndarray:
        try:
            with open(self.file_path, "rb") as fh:
                return np.fromfile(fh, dtype=np.complex64)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error fetching IQ data, received {e}.")