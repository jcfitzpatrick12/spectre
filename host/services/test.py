# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER =  getLogger(__name__)

import numpy as np
from dataclasses import dataclass

from spectre.logging import log_call
from spectre.chunks import Chunks
from spectre.spectrograms.analytical import (
    TestResults,
    validate_analytically
)
from spectre.file_handlers.configs import CaptureConfig


@log_call(_LOGGER)
def analytical(
    tag: str,
    absolute_tolerance: float
) -> dict[str, TestResults]:
    capture_config = CaptureConfig(tag)
    
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