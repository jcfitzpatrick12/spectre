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

    print(deleted_file_names)
    return {"deleted_file_names": deleted_file_names}


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
    
    for chunk in chunks:
        for extension in extensions:
            if chunk.has_file(extension):
                chunk.delete_file(extension)
                _LOGGER.info(f"File deleted: {chunk.get_file(extension).file_path}")


@log_call
def fits_config(tag: str,
) -> None:
    fits_config = FitsConfig(tag)
    fits_config.delete()
    _LOGGER.info(f"File deleted: {fits_config.file_path}")


@log_call
def capture_config(tag: str,
) -> None:
    capture_config = CaptureConfig(tag)
    capture_config.delete()
    _LOGGER.info(f"File deleted: {capture_config.file_path}")