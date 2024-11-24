# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import List, Optional

from spectre.receivers.factory import get_receiver
from spectre.file_handlers.configs import FitsConfig
from spectre.logging import log_call


@log_call(_LOGGER)
def fits_config(tag: str,
                params: Optional[List[str]] = None,
) -> None:
    if params is None:
        params = []
    fits_config = FitsConfig(tag)
    fits_config.save_params(params)
    _LOGGER.info(f"The fits-config for tag: {tag} has been created")


@log_call(_LOGGER)
def capture_config(tag: str,
                   receiver_name: str,
                   mode: str,
                   params: Optional[List[str]]
) -> None:
    if params is None:
        params = []
    receiver = get_receiver(receiver_name, 
                            mode = mode)
    receiver.save_params(params,
                         tag)
    _LOGGER.info(f"The capture-config for tag: {tag} has been created")