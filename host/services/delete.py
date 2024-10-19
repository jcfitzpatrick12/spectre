# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from spectre.logging import LogHandlers
from spectre.chunks import Chunks
from spectre.logging import log_service_call
from spectre.file_handlers.json import (
    FitsConfigHandler,
    CaptureConfigHandler
)


@log_service_call(_LOGGER)
def logs(process_type: str | None = None,
         year: int | None = None,
         month: int | None = None,
         day: int | None = None,
         suppress_doublecheck: bool = False
) -> None:
    log_handlers = LogHandlers(process_type,
                               year,
                               month,
                               day)
    for log_handler in log_handlers:
        # if process type is specified, disregard all logs of differing process types
        if process_type and log_handler.process_type != process_type:
            continue
        if suppress_doublecheck:
            doublecheck_delete = False
        else:
            doublecheck_delete = True
        log_handler.delete(doublecheck_delete=doublecheck_delete)
        _LOGGER.info(f"File deleted: {log_handler.file_path}")


@log_service_call(_LOGGER)
def chunks(tag: str,
           extensions: list[str],
           year: int | None = None,
           month: int | None = None,
           day: int | None = None,
           suppress_doublecheck: bool = False
) -> None:
    chunks = Chunks(tag, 
                    year=year, 
                    month=month,
                    day=day)
    
    for chunk in chunks:
        if suppress_doublecheck:
            doublecheck_delete = False
        else:
            doublecheck_delete = True
        for extension in extensions:
            if chunk.has_file(extension):
                chunk.delete_file(extension, doublecheck_delete=doublecheck_delete)
                _LOGGER.info(f"File deleted: {chunk.get_file(extension).file_path}")


def fits_config(tag: str,
) -> None:
    fits_config_handler = FitsConfigHandler(tag)
    fits_config_handler.delete()
    _LOGGER.info(f"File deleted: {fits_config_handler.file_path}")


def capture_config(tag: str,
) -> None:
    capture_config_handler = CaptureConfigHandler(tag)
    capture_config_handler.delete()
    _LOGGER.info(f"File deleted: {capture_config_handler.file_path}")