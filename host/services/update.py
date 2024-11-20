# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import List

from spectre.receivers.factory import get_receiver
from spectre.chunks import Chunks
from spectre.logging import log_service_call
from spectre.exceptions import ChunkExistsError
from spectre.file_handlers.json_configs import (
    FitsConfigHandler,
    CaptureConfigHandler,
    type_cast_params,
    validate_against_type_template
)

def _has_chunks(tag: str) -> bool:
    """Returns True if any files exist under the input tag."""
    chunks = Chunks(tag)
    return (len(chunks.chunk_list) > 0)


def _caution_update(tag: str,
                    force: bool) -> None:
    """Caution the user if chunks exist under the input tag."""
    if _has_chunks(tag):
        if force:
            _LOGGER.warning(f"Chunks exist under the tag {tag}, forcing update")
            return
        else:
            error_message = (f"Chunks exist under the tag {tag}. "
                             f"It is recommended to create a new tag for any configuration file updates. " 
                             f"Override this functionality with --force. "
                             f"Aborting update")
            _LOGGER.error(error_message)
            raise ChunkExistsError(error_message)


@log_service_call(_LOGGER)
def capture_config(tag: str,
                   params: List[str],
                   force: bool = False,
) -> None: 
    _caution_update(tag, force)

    capture_config_handler = CaptureConfigHandler(tag)
    capture_config = capture_config_handler.read()

    receiver_name = capture_config.get("receiver")
    mode = capture_config.get("mode")
    receiver = get_receiver(receiver_name, mode)

    d = type_cast_params(params, 
                         receiver.type_template)
    capture_config.update(d)

    receiver.save_capture_config(capture_config, 
                                 tag, 
                                 doublecheck_overwrite=False)

    _LOGGER.info(f"Capture config for tag: {tag} has been successfully updated")


@log_service_call(_LOGGER)
def fits_config(tag: str,
                params: List[str],
                force: bool = False,
) -> None:
    _caution_update(tag, force)
    fits_config_handler = FitsConfigHandler(tag)
    fits_config = fits_config_handler.read()

    d = type_cast_params(params,
                         fits_config_handler.template)
    fits_config.update(d)
    
    validate_against_type_template(fits_config, fits_config_handler.template)

    fits_config_handler.save(fits_config, 
                             doublecheck_overwrite = False)

    _LOGGER.info(f"Fits config for tag: {tag} has been successfully updated")