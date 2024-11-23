# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER =  getLogger(__name__)

import numpy as np
from dataclasses import dataclass

from spectre.logging import log_call
from spectre.chunks import Chunks
from spectre.spectrograms.analytical import get_analytical_spectrogram
from spectre.spectrograms.spectrogram import Spectrogram
from spectre.file_handlers.json_configs import CaptureConfigHandler

@dataclass
class TestResults:
    # Whether the times array matches analytically
    times_validated: bool = False  
    # Whether the frequencies array matches analytically
    frequencies_validated: bool = False  
    # Maps each time to whether the corresponding spectrum matched analytically
    spectrum_validated: dict[float, bool] = None

    @property
    def num_validated_spectrums(self) -> int:
        """Counts the number of validated spectrums."""
        return sum(is_validated for is_validated in self.spectrum_validated.values())

    @property
    def num_invalid_spectrums(self) -> int:
        """Counts the number of spectrums that are not validated."""
        return len(self.spectrum_validated) - self.num_validated_spectrums


def _close_enough(ar: np.ndarray, 
                  ar_comparison: np.ndarray,
                  absolute_tolerance: float) -> bool:
    """Close enough accounts for wiggle-room equating floats."""
    return np.all(np.isclose(ar, 
                             ar_comparison, 
                             atol=absolute_tolerance))


def validate_analytically(spectrogram: Spectrogram,
                          capture_config: dict,
                          absolute_tolerance: float) -> TestResults:

    analytical_spectrogram = get_analytical_spectrogram(spectrogram.num_times,
                                                        capture_config)


    test_results = TestResults()

    if _close_enough(analytical_spectrogram.times,
                         spectrogram.times,
                         absolute_tolerance):
        test_results.times_validated = True


    if _close_enough(analytical_spectrogram.frequencies,
                         spectrogram.frequencies,
                         absolute_tolerance):
        test_results.frequencies_validated = True

    test_results.spectrum_validated = {}
    for i in range(spectrogram.num_times):
        time = spectrogram.times[i]
        analytical_spectrum = analytical_spectrogram.dynamic_spectra[:, i]
        spectrum = spectrogram.dynamic_spectra[:, i]
        test_results.spectrum_validated[time] = _close_enough(analytical_spectrum, 
                                                               spectrum,
                                                               absolute_tolerance)

    return test_results


@log_call(_LOGGER)
def analytical(
    tag: str,
    absolute_tolerance: float
) -> dict[str, TestResults]:
    capture_config_handler = CaptureConfigHandler(tag)
    capture_config = capture_config_handler.read()
    
    results_per_chunk = {}
    chunks = Chunks(tag)
    for chunk in chunks:
        if chunk.has_file("fits"):
            chunk_file = chunk.get_file("fits")
            spectrogram = chunk_file.read()
            results_per_chunk[chunk_file.file_name] = validate_analytically(spectrogram, 
                                                                            capture_config,
                                                                            absolute_tolerance)

    return results_per_chunk