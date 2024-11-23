# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER =  getLogger(__name__)

from host.services import capture

from spectre.receivers.factory import get_receiver
from spectre.logging import log_service_call
from spectre.file_handlers.json_configs import CaptureConfigHandler

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
    
    capture_config_handler = CaptureConfigHandler(tag)
    capture_config = capture_config_handler.read()

    receiver_name = capture_config['receiver']
    if receiver_name != "test":
        raise ValueError((f"Tag must correspond to a test receiver. "
                          f"Found receiver {receiver_name} in the capture config for tag {tag}"))

    mode = capture_config['mode']

    # generate spectrograms 
    capture.session(receiver_name,
                    mode,
                    tag,
                    seconds = seconds,
                    minutes = minutes,
                    hours = hours)
    return