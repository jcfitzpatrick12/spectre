# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER =  getLogger(__name__)

from os import listdir, walk
from os.path import splitext
from typing import Any, Optional

from spectre_core.receivers.factory import get_receiver
from spectre_core.receivers.receiver_register import list_all_receiver_names
from spectre_core.chunks import Chunks
from spectre_core.chunks.base import ChunkFile
from spectre_core.cfg import (
    JSON_CONFIGS_DIR_PATH,
    CALLISTO_INSTRUMENT_CODES,
    get_chunks_dir_path
)
from spectre_core.logging import (
    LogHandlers, 
    LogHandler,
    log_call
)
from spectre_core.file_handlers.configs import (
    FitsConfig,
    CaptureConfig
)


@log_call
def callisto_instrument_codes(
) -> list[str]:
    """Get all defined CALLISTO instrument codes"""
    return CALLISTO_INSTRUMENT_CODES


@log_call
def log_file_names(process_type: Optional[str] = None,
                   year: Optional[int] = None,
                   month: Optional[int] = None,
                   day: Optional[int] = None,
) -> list[str]:
    """Get all log file names
    
    Optional filtering by date.
    """
    log_handlers = LogHandlers(process_type,
                               year,
                               month,
                               day)
    return [log_handler.file_name for log_handler in log_handlers.log_handler_list]


@log_call
def chunk_file_names(tag: str,
                     year: Optional[int] = None,
                     month: Optional[int] = None,
                     day: Optional[int] = None,
                     extensions: Optional[list[str]] = None,
) -> list[str]:
    """Get a list of all chunk file sunder the given tag. 
    
    Optional filtering by date and by extension.
    """
    if extensions is None:
        extensions = []
    chunks = Chunks(tag, 
                    year=year, 
                    month=month,
                    day=day)
    chunk_files = []
    for chunk in chunks:
        # if no extensions are specified, look for ALL defined extensions for that chunk
        if not extensions:
            extensions = chunk.extensions

        for extension in extensions:
            if chunk.has_file(extension):
                chunk_file = chunk.get_file(extension)
                chunk_files.append(chunk_file.file_name)
    return chunk_files
    

@log_call
def receiver_names(
) -> list[str]:
    """Get all defined receiver names"""
    return list_all_receiver_names()


@log_call
def receiver_modes(receiver_name: str,
) -> list[str]:
    """For the input receiver, get all the defined modes"""
    receiver = get_receiver(receiver_name)
    return receiver.valid_modes


@log_call
def receiver_specifications(receiver_name: str,
) -> dict[str, Any]:
    """For the input receiver, get the corresponding specifications"""
    receiver = get_receiver(receiver_name)
    return receiver.specifications


@log_call
def fits_config_file_names(
) -> list[str]:
    """Get the file names for all defined fits configs"""
    return [file_name for file_name in listdir(JSON_CONFIGS_DIR_PATH) if file_name.startswith("fits_config")]


@log_call
def capture_config_file_names(
) -> list[str]:
    """Get the file names for all defined capture configs"""
    return [file_name for file_name in listdir(JSON_CONFIGS_DIR_PATH) if file_name.startswith("capture_config")]   


@log_call
def tags(year: Optional[int] = None,
         month: Optional[int] = None,
         day: Optional[int] = None,
) -> list[str]:
    """Get a list of all unique tags, with corresponding chunk files"""
    chunks_dir_path = get_chunks_dir_path(year, month, day)
    chunk_files = [f for (_, _, files) in walk(chunks_dir_path) for f in files]
    tags = set()
    for chunk_file in chunk_files:
        chunk_base_name, _ = splitext(chunk_file)
        tag = chunk_base_name.split("_")[1]
        tags.add(tag)
    return sorted(list(tags))


@log_call
def log_contents(pid: Optional[str] = None,
                 file_name: Optional[str] = None
) -> str:
    """Get the contents of a log according to the process ID or by file name directly"""
    # Ensure that exactly one of --pid or --file-name is specified
    if not (bool(pid) ^ bool(file_name)):
        raise ValueError("Exactly one of --pid or --file-name must be specified")
    
    log_handlers = LogHandlers()
    if pid:
        log_handler = log_handlers.get_log_handler_from_pid(pid)
    if file_name:
        log_handler = log_handlers.get_log_handler_from_file_name(file_name)

    return log_handler.read()


@log_call
def fits_config_type_template(tag: Optional[str] = None,
                              as_command: bool = False
) -> dict[str, Any] | str:
    """Get the type template for the fits config with a given tag.
    
    Optionally, format the return as a command to create a fits config with the input tag.
    """
    if as_command:
        if not tag:
            raise ValueError("If specifying --as-command, the tag must also be specified with --tag or -t")
        fits_config = FitsConfig(tag)
        return fits_config.get_create_fits_config_cmd(tag, 
                                                      as_string = True)
    else:
        return FitsConfig.type_template


@log_call
def type_template(receiver_name: str,
                  mode: str,
                  as_command: bool = False,
                  tag: Optional[str] = None
) -> dict[str, Any] | str:
    """Get the type template for a capture config for a receiver operating in a particular mode.
    
    Optionally, format the return as a command to create a capture config with the input tag.
    """
    receiver = get_receiver(receiver_name, 
                            mode = mode)
    if as_command:
        if not tag:
            raise ValueError("If specifying --as-command, the tag must also be specified with --tag or -t")
        return receiver.get_create_capture_config_cmd(tag, as_string=True)
    else:
        return receiver.type_template


@log_call
def fits_config_contents(tag: str
) -> dict[str, Any]:
    """Return the contents of a fits config with a given tag."""
    fits_config = FitsConfig(tag)
    return fits_config.dict


@log_call
def capture_config(tag: str
) -> dict[str, Any]:
    """Return the contents of a capture config with a given tag."""
    capture_config = CaptureConfig(tag)
    return capture_config.dict
