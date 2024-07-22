# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from typing import Tuple

from spectre.chunks.ExtChunk import ExtChunk

class HdrChunk(ExtChunk):
    def __init__(self, chunk_start_time: str, tag: str):
        super().__init__(chunk_start_time, tag, ".hdr")

    def read(self) -> Tuple[int, np.ndarray, np.ndarray]:
        try:
            hdr_contents = self._read_file_contents()
            millisecond_correction = self._get_millisecond_correction(hdr_contents)
            center_frequencies = self._get_center_frequencies(hdr_contents)
            num_samples = self._get_num_samples(hdr_contents)
            self._validate_frequencies_and_samples(center_frequencies, num_samples)
            return millisecond_correction, center_frequencies, num_samples

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error fetching IQ data, received {e}.")


    def _read_file_contents(self) -> np.ndarray:
        """Reads the contents of the .hdr file into a NumPy array."""
        with open(self.get_path(), "rb") as fh:
            return np.fromfile(fh, dtype=np.float32)


    def _get_millisecond_correction(self, hdr_contents: np.ndarray) -> int:
        """Extracts and returns the millisecond correction from the file contents."""
        millisecond_correction_as_float = hdr_contents[0]
        if millisecond_correction_as_float.is_integer():
            return int(millisecond_correction_as_float)
        raise ValueError("Millisecond correction value is not an integer.")


    def _get_center_frequencies(self, hdr_contents: np.ndarray) -> np.ndarray:
        """Extracts center frequencies from the file contents."""
        return hdr_contents[1::2]


    def _get_num_samples(self, hdr_contents: np.ndarray) -> np.ndarray:
        """Extracts the number of samples per frequency from the file contents."""
        num_samples_as_float = hdr_contents[2::2]
        if not all(num_samples_as_float == num_samples_as_float.astype(int)):
            raise ValueError("Number of samples per frequency is expected to describe an integer.")
        return num_samples_as_float.astype(int)


    def _validate_frequencies_and_samples(self, center_frequencies: np.ndarray, num_samples: np.ndarray) -> None:
        """Validates that the center frequencies and the number of samples arrays have the same length."""
        if len(center_frequencies) != len(num_samples):
            raise ValueError("Center frequencies and number of samples arrays are not the same length.")
