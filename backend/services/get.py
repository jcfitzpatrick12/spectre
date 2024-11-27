# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER =  getLogger(__name__)

from os import listdir, walk
from os.path import splitext
from typing import Any, Optional

from spectre_radio.receivers.factory import get_receiver
from spectre_radio.receivers.receiver_register import list_all_receiver_names
from spectre_radio.chunks import Chunks
from spectre_radio.chunks.base import ChunkFile
from spectre_radio.cfg import (
    JSON_CONFIGS_DIR_PATH,
    CALLISTO_INSTRUMENT_CODES,
    get_chunks_dir_path
)
from spectre_radio.logging import (
    LogHandlers, 
    LogHandler,
    log_call
)
from spectre_radio.file_handlers.configs import (
    FitsConfig,
    CaptureConfig
)


@log_call(_LOGGER)
def callisto_instrument_codes(
) -> None:
    """Gets all defined CALLISTO instrument codes"""
    return CALLISTO_INSTRUMENT_CODES


@log_call(_LOGGER)
def log_handlers(process_type: Optional[str] = None,
                 year: Optional[int] = None,
                 month: Optional[int] = None,
                 day: Optional[int] = None,
) -> list[LogHandler]:
    log_handlers = LogHandlers(process_type,
                               year,
                               month,
                               day)
    
    return log_handlers.log_handler_list


@log_call(_LOGGER)
def log_file_names(process_type: Optional[str] = None,
                   year: Optional[int] = None,
                   month: Optional[int] = None,
                   day: Optional[int] = None,
) -> list[str]:
    log_handler_list = log_handlers(process_type, year, month, day)
    return [log_handler.file_name for log_handler in log_handler_list]


@log_call(_LOGGER)
def chunk_files(tag: str,
                year: Optional[int] = None,
                month: Optional[int] = None,
                day: Optional[int] = None,
                extensions: Optional[list[str]] = None,
) -> list[ChunkFile]:
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
                chunk_files.append(chunk_file)
    return chunk_files


@log_call(_LOGGER)
def chunk_file_names(tag: str,
                     year: Optional[int] = None,
                     month: Optional[int] = None,
                     day: Optional[int] = None,
                     extensions: Optional[list[str]] = None
) -> list[str]:
    chunk_file_list = chunk_files(tag, year, month, day, extensions)
    return [chunk_file.file_name for chunk_file in chunk_file_list]
    

@log_call(_LOGGER)
def receiver_names(
) -> list[str]:
    return list_all_receiver_names()


@log_call(_LOGGER)
def receiver_modes(receiver_name: str,
) -> list[str]:
    receiver = get_receiver(receiver_name)
    return receiver.valid_modes


@log_call(_LOGGER)
def receiver_specifications(receiver_name: str,
) -> dict[str, Any]:
    receiver = get_receiver(receiver_name)
    return receiver.specifications


@log_call(_LOGGER)
def fits_config_file_names(
) -> list[str]:
    return [file_name for file_name in listdir(JSON_CONFIGS_DIR_PATH) if file_name.startswith("fits_config")]


@log_call(_LOGGER)
def capture_config_names(
) -> list[str]:
    return [file_name for file_name in listdir(JSON_CONFIGS_DIR_PATH) if file_name.startswith("capture_config")]   


@log_call(_LOGGER)
def tags(year: Optional[int] = None,
         month: Optional[int] = None,
         day: Optional[int] = None,
) -> list[str]:
    chunks_dir_path = get_chunks_dir_path(year, month, day)
    chunk_files = [f for (_, _, files) in walk(chunks_dir_path) for f in files]
    tags = set()
    for chunk_file in chunk_files:
        chunk_base_name, _ = splitext(chunk_file)
        tag = chunk_base_name.split("_")[1]
        tags.add(tag)
    return sorted(list(tags))


@log_call(_LOGGER)
def log_handler(pid: Optional[str] = None,
                file_name: Optional[str] = None
) -> LogHandler:
    # Ensure that exactly one of --pid or --file-name is specified
    if not (bool(pid) ^ bool(file_name)):
        raise ValueError("Exactly one of --pid or --file-name must be specified")
    
    log_handlers = LogHandlers()
    if pid:
        return log_handlers.get_log_handler_from_pid(pid)
    if file_name:
        return log_handlers.get_log_handler_from_file_name(file_name)


@log_call(_LOGGER)
def fits_config_type_template(tag: Optional[str] = None,
                              as_command: bool = False
) -> dict[str, Any] | str:
    if as_command:
        if not tag:
            raise ValueError("If specifying --as-command, the tag must also be specified with --tag or -t")
        fits_config = FitsConfig(tag)
        return fits_config.get_create_fits_config_cmd(tag, 
                                                      as_string = True)
    else:
        return FitsConfig.type_template


@log_call(_LOGGER)
def type_template(receiver_name: str,
                  mode: str,
                  as_command: bool = False,
                  tag: Optional[str] = None
) -> dict[str, Any] | str:
    
    receiver = get_receiver(receiver_name, 
                            mode = mode)
    if as_command:
        if not tag:
            raise ValueError("If specifying --as-command, the tag must also be specified with --tag or -t")
        return receiver.get_create_capture_config_cmd(tag, as_string=True)
    else:
        return receiver.type_template


@log_call(_LOGGER)
def fits_config(tag: str
) -> FitsConfig:
    return FitsConfig(tag)


@log_call(_LOGGER)
def capture_config(tag: str
) -> CaptureConfig:
    return CaptureConfig(tag)
