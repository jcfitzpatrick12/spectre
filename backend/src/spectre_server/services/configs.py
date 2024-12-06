# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import List, Optional, Any
from os import listdir

from spectre_core.cfg import CONFIGS_DIR_PATH
from spectre_core.chunks import Chunks
from spectre_core.receivers.factory import get_receiver
from spectre_core.logging import log_call
from spectre_core.file_handlers.configs import (
    FitsConfig,
    CaptureConfig,
    type_cast_params,
    validate_against_type_template
)

@log_call
def get_configs(config_type: Optional[str] = None,
                tag: Optional[str] = None
) -> list[str]:
    """Get the file names for all existing fits configs"""
    file_names = []
    for file_name in listdir(CONFIGS_DIR_PATH):
        if config_type and not file_name.startswith(config_type):
            continue
        if tag and not file_name.endswith(tag):
            continue
        file_names.append(file_name)
    return file_names
 


@log_call
def create_capture_config(tag: str,
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

    return capture_config.file_name


@log_call
def create_fits_config(tag: str,
                       params: Optional[List[str]] = None,
                       force: bool = False,
) -> str:
    """Create a fits-config, and return its file name."""

    if params is None:
        params = []

    fits_config = FitsConfig(tag)
    fits_config.save_params(params,
                            force)
    
    _LOGGER.info(f"The fits-config for tag '{tag}' has been created: {fits_config.file_name}")

    return fits_config.file_name


@log_call
def get_fits_config(tag: str
) -> dict[str, Any]:
    """Return the contents of a fits config with a given tag."""
    fits_config = FitsConfig(tag)
    return fits_config.dict


@log_call
def get_capture_config(tag: str
) -> dict[str, Any]:
    """Return the contents of a capture config with a given tag."""
    capture_config = CaptureConfig(tag)
    return capture_config.dict


@log_call
def delete_fits_config(tag: str,
) -> str:
    fits_config = FitsConfig(tag)
    fits_config.delete()
    _LOGGER.info(f"File deleted: {fits_config.file_name}")
    
    return fits_config.file_name


@log_call
def delete_capture_config(tag: str,
) -> str:
    capture_config = CaptureConfig(tag)
    capture_config.delete()
    _LOGGER.info(f"File deleted: {capture_config.file_name}")
    
    return capture_config.file_name


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
def update_capture_config(tag: str,
                          params: List[str],
                          force: bool = False,
) -> str: 
    
    _caution_update(tag, 
                    force)

    capture_config = CaptureConfig(tag)

    receiver_name = capture_config.get("receiver")
    mode = capture_config.get("mode")
    receiver = get_receiver(receiver_name, mode)

    d = type_cast_params(params, 
                         receiver.type_template)
    
    capture_config.update(d)


    receiver.save_capture_config(capture_config.dict, 
                                 tag, 
                                 force = True)


    _LOGGER.info(f"Capture config for tag: {tag} has been successfully updated: {capture_config.file_name}")

    return capture_config.file_name


@log_call
def update_fits_config(tag: str,
                       params: List[str],
                       force: bool = False,
) -> str:
    
    _caution_update(tag, 
                    force)
    
    fits_config = FitsConfig(tag)

    d = type_cast_params(params,
                         fits_config.type_template)
    fits_config.update(d)
    
    validate_against_type_template(fits_config, fits_config.type_template)

    fits_config.save(fits_config.dict, 
                     force = True)

    _LOGGER.info(f"Fits config for tag: {tag} has been successfully updated: {fits_config.file_name}")

    return fits_config.file_name