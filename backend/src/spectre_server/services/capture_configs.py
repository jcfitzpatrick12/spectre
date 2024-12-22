# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import List, Optional, Any
from os import listdir

from spectre_core.paths import get_configs_dir_path
from spectre_core.chunks import Chunks
from spectre_core.receivers.factory import get_receiver
from spectre_core.logging import log_call
from spectre_core.parameters import parse_string_parameters, make_parameters
from spectre_core.capture_config import CaptureConfig

@log_call
def get_capture_configs(
) -> list[str]:
    """Get the file names for all existing fits configs"""
    return listdir( get_configs_dir_path() )
 


@log_call
def create_capture_config(tag: str,
                          receiver_name: str,
                          mode: str,
                          string_parameters: Optional[list[str]] = None,
                          force: bool = False
) -> str:
    """Create a capture config and return its file name."""
    if string_parameters is None:
        string_parameters = []
        
    receiver = get_receiver(receiver_name, 
                            mode = mode)
    
    parameters = make_parameters( parse_string_parameters(string_parameters) )

    receiver.save_parameters(tag,
                             parameters,
                             force)
    
    # create an instance of the newly created capture config
    capture_config = CaptureConfig(tag)
    
    _LOGGER.info(f"The capture-config for tag '{tag}' has been created: {capture_config.file_name}")

    return capture_config.file_name


@log_call
def get_capture_config(tag: str
) -> dict[str, Any]:
    """Return the contents of a capture config with a given tag."""
    capture_config = CaptureConfig(tag)
    return capture_config.to_dict()



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
            error_message = (f"Chunks exist under the tag {tag}. Any updates may lead to undefined behaviour. "
                             f"It is recommended to create a new tag for any configuration file updates. " 
                             f"Override this functionality with --force. Aborting update")
            _LOGGER.error(error_message)
            raise FileExistsError(error_message)
        

@log_call
def update_capture_config(tag: str,
                          string_parameters: List[str],
                          force: bool = False,
) -> str: 
    
    _caution_update(tag, 
                    force)

    capture_config = CaptureConfig(tag)

    receiver = get_receiver(capture_config.receiver_name,
                            capture_config.receiver_mode)
    
    parameters = make_parameters( parse_string_parameters(string_parameters) )
    for parameter in parameters:
        capture_config.parameters.add_parameter(parameter, 
                                                force=True)

    receiver.save_parameters(tag,
                             parameters,)


    _LOGGER.info(f"Capture config for tag: {tag} has been successfully updated: {capture_config.file_name}")

    return capture_config.file_name