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
from spectre.file_handlers.json import (
    FitsConfigHandler,
    CaptureConfigHandler
)

def _has_chunks(tag: str) -> bool:
    """Returns true if any files exist under the input tag. """
    chunks = Chunks(tag)
    return len(chunks.chunk_list)


def _caution_update(tag: str,
                    force: bool) -> None:
    """"""
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
    # extract the current capture config saved (which will be type cast!)
    capture_config_handler = CaptureConfigHandler(tag)
    capture_config = capture_config_handler.read()

    # find the receiver and the mode of the capture config
    receiver_name = capture_config.get("receiver")
    mode = capture_config.get("mode")

    # and use them to instantiate a receiver
    receiver = get_receiver(receiver_name, mode)
    # fetch the corresponding template so we can type cast the params list
    # convert the params to update (passed in via --param arguments) into a string valued dict
    d = capture_config_handler.type_cast_params(params, 
                                                receiver.template, 
                                                validate_against_template=False, # don't validate against the template
                                                ignore_keys=['receiver', 'mode', 'tag'])
    # update the key values as per the params dict
    capture_config.update(d)
    # save the updated capture config
    receiver.save_capture_config(tag, capture_config, doublecheck_overwrite=False)
    _LOGGER.info(f"Capture config for tag: {tag} has been successfully updated")


@log_service_call(_LOGGER)
def fits_config(tag: str,
                params: List[str],
                force: bool = False,
) -> None:
    _caution_update(tag, force)
    fits_config_handler = FitsConfigHandler(tag)
    fits_config = fits_config_handler.read()
    d = fits_config_handler.type_cast_params(params,
                                             fits_config_handler.template,
                                             validate_against_template=False)
    fits_config.update(d)
    fits_config_handler.validate_against_template(fits_config, fits_config_handler.template)
    fits_config_handler.save(fits_config, doublecheck_overwrite=False)
    _LOGGER.info(f"Fits config for tag: {tag} has been successfully updated")