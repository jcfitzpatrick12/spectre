# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import List, Optional

from spectre_core.receivers.factory import get_receiver
from spectre_core.file_handlers.configs import FitsConfig, CaptureConfig
from spectre_core.logging import log_call


@log_call
def fits_config(tag: str,
                params: Optional[List[str]] = None,
                force: bool = False,
) -> dict[str, str]:
    """Create a fits-config, and return its file name."""

    if params is None:
        params = []

    fits_config = FitsConfig(tag)
    fits_config.save_params(params,
                            force)
    
    _LOGGER.info(f"The fits-config for tag '{tag}' has been created: {fits_config.file_name}")

    return {"file_name": fits_config.file_name}

@log_call
def capture_config(tag: str,
                   receiver_name: str,
                   mode: str,
                   params: Optional[List[str]],
                   force: bool = False
) -> str:
    """Create a capture config and return its file name."""
    if params is None:
        params = []
        
    receiver = get_receiver(receiver_name, 
                            mode = mode)
    receiver.save_params(params,
                         tag,
                         force)
    
    # create an instance of the newly created capture config
    capture_config = CaptureConfig(tag)
    
    _LOGGER.info(f"The capture-config for tag '{tag}' has been created: {capture_config.file_name}")

    return {"file_name": capture_config.file_name}