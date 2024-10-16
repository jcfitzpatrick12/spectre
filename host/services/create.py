# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import List

from spectre.receivers.factory import get_receiver
from spectre.file_handlers.json.handlers import FitsConfigHandler
from spectre.logging import log_service_call


@log_service_call(_LOGGER)
def fits_config(tag: str,
                params: List[str] | None = None,
) -> None:
    if params is None:
        params = []
    fits_config_handler = FitsConfigHandler(tag)
    fits_config_handler.save_params_as_fits_config(params)
    _LOGGER.info(f"The fits-config for tag \"{tag}\" has been created")


@log_service_call(_LOGGER)
def capture_config(tag: str,
                   receiver_name: str,
                   mode: str,
                   params: List[str] | None
) -> None:
    if params is None:
        params = []
    receiver = get_receiver(receiver_name, mode = mode)
    receiver.save_params_as_capture_config(tag, params)
    _LOGGER.info(f"The capture-config for tag \"{tag}\" has been created")