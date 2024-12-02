# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import List

from spectre_core.receivers.factory import get_receiver
from spectre_core.chunks import Chunks
from spectre_core.logging import log_call
from spectre_core.file_handlers.configs import (
    FitsConfig,
    CaptureConfig,
    type_cast_params,
    validate_against_type_template
)

def _has_chunks(tag: str
) -> bool:
    """Returns True if any files exist under the input tag."""
    chunks = Chunks(tag)
    return (len(chunks.chunk_list) > 0)


def _caution_update(tag: str,
                    force: bool
) -> None:
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
            raise FileExistsError(error_message)


@log_call
def capture_config(tag: str,
                   params: List[str],
                   force: bool = False,
) -> None: 
    _caution_update(tag, force)

    capture_config = CaptureConfig(tag)

    receiver_name = capture_config.get("receiver")
    mode = capture_config.get("mode")
    receiver = get_receiver(receiver_name, mode)

    d = type_cast_params(params, 
                         receiver.type_template)
    capture_config.update(d)

    receiver.save_capture_config(capture_config.dict, 
                                 tag, 
                                 doublecheck_overwrite=False)

    _LOGGER.info(f"Capture config for tag: {tag} has been successfully updated")


@log_call
def fits_config(tag: str,
                params: List[str],
                force: bool = False,
) -> None:
    _caution_update(tag, force)
    fits_config = FitsConfig(tag)

    d = type_cast_params(params,
                         fits_config.type_template)
    fits_config.update(d)
    
    validate_against_type_template(fits_config, fits_config.type_template)

    fits_config.save(fits_config.dict, 
                     doublecheck_overwrite = False)

    _LOGGER.info(f"Fits config for tag: {tag} has been successfully updated")