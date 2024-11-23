# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER =  getLogger(__name__)

from typing import Any

from host.services import capture

from spectre.logging import log_service_call
from spectre.chunks import Chunks
from spectre.spectrograms.analytical import validate_analytically
from spectre.file_handlers.json_configs import CaptureConfigHandler

def _validate_analytically(tag: str) -> None:
    capture_config_handler = CaptureConfigHandler(tag)
    capture_config = capture_config_handler.read()

    chunks = Chunks(tag)
    for chunk in chunks:
        if chunk.has_file("fits"):
            spectrogram = chunk.read_file("fits")
            validate_analytically(spectrogram, 
                                  capture_config)



@log_service_call(_LOGGER)
def end_to_end(
    tag: str,
    seconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
) -> None:
    """Do an end-to-end using the test receiver.
    
    Generates spectrograms for a time defined by the user.
    For all those created, compares to the corresponding 
    analytically derived solution.
    """
    
    # generate live data from the test receiver
    capture.session(tag,
                    seconds = seconds,
                    minutes = minutes,
                    hours = hours)

    # compare the results generated to the analytically
    # derived solutions
    _validate_analytically(tag)
    return