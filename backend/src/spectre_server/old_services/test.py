# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from typing import Any

from spectre_core.logging import log_call
from spectre_core.chunks import Chunks
from spectre_core.spectrograms.analytical import validate_analytically
from spectre_core.file_handlers.configs import CaptureConfig


@log_call
def analytical(
    tag: str,
    absolute_tolerance: float
) -> dict[str, dict[str, Any]]:
    capture_config = CaptureConfig(tag)
    
    results_per_chunk = {}
    chunks = Chunks(tag)
    for chunk in chunks:
        if chunk.has_file("fits"):
            chunk_file = chunk.get_file("fits")
            spectrogram = chunk_file.read()
            test_results = validate_analytically(spectrogram, 
                                                 capture_config,
                                                 absolute_tolerance)
            results_per_chunk[chunk_file.file_name] = test_results.jsonify()

    return results_per_chunk