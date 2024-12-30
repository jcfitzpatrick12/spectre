# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import List, Optional, Any
from os import listdir

from spectre_core.config import get_configs_dir_path
from spectre_core.batches import Batches
from spectre_core.receivers import get_receiver
from spectre_core.logging import log_call
from spectre_core.capture_configs import CaptureConfig, parse_string_parameters, make_parameters


@log_call
def get_capture_configs(
) -> list[str]:
    """Get the file names for all existing fits configs"""
    return listdir( get_configs_dir_path() )
 


@log_call
def create_capture_config(tag: str,
                          receiver_name: str,
                          receiver_mode: str,
                          string_parameters: Optional[list[str]] = None,
                          force: bool = False
) -> str:
    """Create a capture config and return its file name."""
    if string_parameters is None:
        string_parameters = []
        
    receiver = get_receiver(receiver_name, 
                            mode = receiver_mode)
    
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
    return capture_config.dict



@log_call
def delete_capture_config(tag: str,
) -> str:
    capture_config = CaptureConfig(tag)
    capture_config.delete()
    _LOGGER.info(f"File deleted: {capture_config.file_name}")
    
    return capture_config.file_name


def _has_batches(tag: str
) -> bool:
    """Returns True if any files exist under the input tag."""
    batches = Batches(tag)
    return (len(batches.batch_list) > 0)


def _caution_update(tag: str,
                    force: bool
) -> None:
    """Caution the user if batches exist under the input tag."""
    if _has_batches(tag):
        if force:
            _LOGGER.warning(f"Batches exist under the tag {tag}, forcing update")
            return
        else:
            error_message = (f"Batches exist under the tag {tag}. Any updates may lead to undefined behaviour. "
                             f"It is recommended to create a new tag for any configuration file updates. " 
                             f"Override this functionality with --force. Aborting update")
            _LOGGER.error(error_message)
            raise FileExistsError(error_message)
        

@log_call
def update_capture_config(tag: str,
                          string_parameters: list[str],
                          force: bool = False,
) -> str: 
    
    _caution_update(tag, 
                    force)
    
    new_parameters = make_parameters( parse_string_parameters(string_parameters) )

    capture_config = CaptureConfig(tag)
    
    parameters = make_parameters( parse_string_parameters(string_parameters) )
    for parameter in parameters:
        capture_config.parameters.add_parameter(parameter, 
                                                force=True)

    receiver = get_receiver(capture_config.receiver_name,
                            capture_config.receiver_mode)
    receiver.save_parameters(tag,
                             capture_config.parameters,
                             force=True)


    _LOGGER.info(f"Capture config for tag: {tag} has been successfully updated: {capture_config.file_name}")

    return capture_config.file_name