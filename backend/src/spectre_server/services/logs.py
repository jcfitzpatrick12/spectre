# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import Optional

from spectre_core.logging import LogHandlers
from spectre_core.logging import log_call


@log_call
def delete_logs(process_type: str = None,
                year: Optional[int] = None,
                month: Optional[int] = None,
                day: Optional[int] = None
        ) -> dict[str, list[str]]:
    """Delete log files.
    
    Filter deletion according to the process type and date.
    """
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
def get_logs(process_type: Optional[str] = None,
             year: Optional[int] = None,
             month: Optional[int] = None,
             day: Optional[int] = None,
) -> list[str]:
    """Get the file names of all existing logs.
    
    Optional filtering by date.
    """
    log_handlers = LogHandlers(process_type,
                               year,
                               month,
                               day)
    return [log_handler.file_name for log_handler in log_handlers.log_handler_list]


@log_call
def get_log(pid: Optional[str] = None
) -> str:
    """Get the contents of a log according to the process ID"""
    log_handlers = LogHandlers()
    log_handler = log_handlers.get_from_pid(pid)
    return log_handler.read()