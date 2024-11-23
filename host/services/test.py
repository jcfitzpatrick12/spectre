# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER =  getLogger(__name__)

import numpy as np
import typer

from host.services import capture

from spectre.logging import log_service_call
from spectre.chunks import Chunks
from spectre.spectrograms.analytical import get_analytical_spectrogram
from spectre.spectrograms.spectrogram import Spectrogram
from spectre.file_handlers.json_configs import CaptureConfigHandler


def _close_enough(ar: np.ndarray, 
                  ar_comparison: np.ndarray) -> bool:

    return np.all(np.isclose(ar, 
                             ar_comparison, 
                             atol=1e-4))


def validate_analytically(spectrogram: Spectrogram,
                          capture_config: dict) -> None:
    
    # check that capture config was created by a test receiver
    receiver_name, test_mode = capture_config["receiver"], capture_config["mode"]
    if receiver_name != "test":
        raise ValueError(f"Expected a capture config created by a test receiver, but found {receiver_name}")
    
    # build the corresponding analytical spectrogram
    analytical_spectrogram = get_analytical_spectrogram(test_mode,
                                                        spectrogram.num_spectrums,
                                                        capture_config)


    # # compare results
    if not _close_enough(analytical_spectrogram.times,
                         spectrogram.times):
        raise ValueError(f"Analytical validation has failed! Mismatch in times.")
    
    exit()
    # if not _close_enough(analytical_spectrogram.frequencies,
    #                      spectrogram.frequencies):
    #     raise ValueError(f"Analytical validation has failed! Mismatch in frequencies.")

    
    # for t in list(spectrogram.times):
    #     analytical_frequency_cut = analytical_spectrogram.get_frequency_cut(t)
    #     test_frequency_cut = spectrogram.get_frequency_cut(t)
    #     if not _close_enough(analytical_frequency_cut.cut, 
    #                          test_frequency_cut.cut):
    #         raise ValueError(f"Analytical validation has failed! Mismatch in dynamic spectra.")
    
    exit()


@log_service_call(_LOGGER)
def end_to_end(
    tag: str
) -> None:
    """Do an end-to-end using the test receiver.
    
    Generates spectrograms for a time defined by the user.
    For all those created, compares to the corresponding 
    analytically derived solution.
    """
    capture_config_handler = CaptureConfigHandler(tag)
    capture_config = capture_config_handler.read()

    chunks = Chunks(tag)
    for chunk in chunks:
        if chunk.has_file("fits"):
            chunk_file = chunk.get_file("fits")
            _LOGGER.info(f"Validating {chunk_file.file_name}")
            spectrogram = chunk_file.read()
            validate_analytically(spectrogram, 
                                  capture_config)