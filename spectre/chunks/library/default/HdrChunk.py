# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from typing import Tuple

from spectre.chunks.ChunkFile import ChunkFile

class HdrChunk(ChunkFile):
    def __init__(self, chunk_start_time: str, tag: str):
        super().__init__(chunk_start_time, tag, "hdr")


    def read(self) -> int:
        try:
            hdr_contents = self._read_file_contents()
            return self._get_millisecond_correction(hdr_contents)

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error fetching IQ data, received {e}.")


    def _read_file_contents(self) -> np.ndarray:
        # Reads the contents of the .hdr file into a NumPy array 
        with open(self.file_path, "rb") as fh:
            return np.fromfile(fh, dtype=np.float32)


    def _get_millisecond_correction(self, hdr_contents: np.ndarray) -> int:
        # Validates that the header file contains exactly one element 
        if len(hdr_contents) != 1:
            raise ValueError(f"Only expected one integer in the header, but received header contents: {hdr_contents}")
        # Extracts and returns the millisecond correction from the file contents 
        millisecond_correction_as_float = float(hdr_contents[0])
        if millisecond_correction_as_float.is_integer():
            return int(millisecond_correction_as_float)
        raise ValueError(f"Millisecond correction is expected to describe an integer, but received {millisecond_correction_as_float}")
