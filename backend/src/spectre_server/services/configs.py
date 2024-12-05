# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import List, Optional, Any
from os import listdir

from spectre_core.cfg import JSON_CONFIGS_DIR_PATH
from spectre_core.receivers.factory import get_receiver
from spectre_core.file_handlers.configs import FitsConfig, CaptureConfig
from spectre_core.logging import log_call

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
) -> dict[str, str]:
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
) -> None:
    fits_config = FitsConfig(tag)
    fits_config.delete()
    _LOGGER.info(f"File deleted: {fits_config.file_name}")
    
    return fits_config.file_name


@log_call
def delete_capture_config(tag: str,
) -> None:
    capture_config = CaptureConfig(tag)
    capture_config.delete()
    _LOGGER.info(f"File deleted: {capture_config.file_name}")
    
    return capture_config.file_name


@log_call
def get_capture_config_type_template(receiver_name: str,
                                     mode: str
) -> dict[str, Any]:
    """Get the type template for a capture config for a receiver operating in a particular mode.
    
    Optionally, format the return as a command to create a capture config with the input tag.
    """
    receiver = get_receiver(receiver_name, 
                            mode = mode)
    
    return {k: v.__name__ for k, v in receiver.type_template.items()}


@log_call
def get_fits_config_type_template(
) -> dict[str, Any]:
    """Get the type template for the fits config with a given tag."""
    return {k: v.__name__ for k, v in FitsConfig.type_template}


@log_call
def get_fits_configs(
) -> list[str]:
    """Get the file names for all existing fits configs"""
    return [file_name for file_name in listdir(JSON_CONFIGS_DIR_PATH) if file_name.startswith("fits_config")]


@log_call
def get_capture_configs(
) -> list[str]:
    """Get the file names for all existing capture configs"""
    return [file_name for file_name in listdir(JSON_CONFIGS_DIR_PATH) if file_name.startswith("capture_config")]  
