# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import Optional

from spectre_core.logging import LogHandlers
from spectre_core.chunks import Chunks
from spectre_core.logging import log_call
from spectre_core.file_handlers.configs import (
    FitsConfig,
    CaptureConfig
)


@log_call
def logs(process_type: str = None,
         year: Optional[int] = None,
         month: Optional[int] = None,
         day: Optional[int] = None
) -> dict[str, list[str]]:
    log_handlers = LogHandlers(process_type,
                               year,
                               month,
                               day)
    deleted_file_names = []
    for log_handler in log_handlers:
        # if process type is specified, disregard all logs of differing process types
        if process_type and log_handler.process_type != process_type:
            continue
        log_handler.delete()
        _LOGGER.info(f"File deleted: {log_handler.file_path}")
        deleted_file_names.append(log_handler.file_name)

    return deleted_file_names


@log_call
def chunk_files(tag: str,
                extensions: list[str],
                year: Optional[int] = None,
                month: Optional[int] = None,
                day: Optional[int] = None,
) -> None:
    chunks = Chunks(tag, 
                    year=year, 
                    month=month,
                    day=day)
    
    deleted_file_names = []
    for chunk in chunks:
        for extension in extensions:
            if chunk.has_file(extension):
                chunk_file = chunk.get_file(extension)
                chunk_file.delete()
                _LOGGER.info(f"File deleted: {chunk_file.file_name}")
                deleted_file_names.append(chunk_file.file_name)

    return deleted_file_names


@log_call
def fits_config(tag: str,
) -> None:
    fits_config = FitsConfig(tag)
    fits_config.delete()
    _LOGGER.info(f"File deleted: {fits_config.file_name}")
    
    return fits_config.file_name

@log_call
def capture_config(tag: str,
) -> None:
    capture_config = CaptureConfig(tag)
    capture_config.delete()
    _LOGGER.info(f"File deleted: {capture_config.file_name}")
    
    return capture_config.file_name