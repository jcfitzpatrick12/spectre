# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import Optional

from spectre_core.logs import Logs, ProcessType, log_call
from spectre_core.config import trim_spectre_data_dir_path

@log_call
def delete_logs(
    process_type: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None
) -> list[str]:
    """Delete log files.

    :param process_type: Only delete logs with a particular process type. If no process type is given,
    then log files with any process type will be deleted. Defaults to None
    :param year: Delete only log files from this numeric year. Defaults to None. If no year, month, 
    or day is specified, files from any year will be deleted.
    :param month: Delete only log files from this numeric month. Defaults to None. If a year is 
    specified but not a month, all files from that year will be deleted.
    :param day: Delete only log files from this numeric day. Defaults to None. If both year and month 
    are specified but not a day, all files from that year and month will be deleted.
    :return: The file paths of all logs which were deleted, relative to `SPECTRE_DATA_DIR_PATH`.
    """
    proc_type = ProcessType(process_type) if process_type is not None else None
    logs = Logs(proc_type,
                year,
                month,
                day)
    deleted_file_names = []
    for log in logs:
        # if process type is specified, disregard all logs of differing process types
        if process_type and log.process_type != process_type:
            continue
        log.delete()
        _LOGGER.info(f"File deleted: {log.file_path}")
        deleted_file_names.append( trim_spectre_data_dir_path(log.file_path) )

    return deleted_file_names


@log_call
def get_logs(
    process_type: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> list[str]:
    """Get the file names of all logs which exist in the file system.

    :param process_type: Filter logs by their process type, defaults to None
    :param year: Filter logs by the numeric year, defaults to None
    :param month: Filter logs by the numeric month, defaults to None
    :param day: Filter logs by the numeric day, defaults to None
    :return: The file paths of logs which exist in the file system, relative to `SPECTRE_DATA_DIR_PATH`.
    """
    proc_type = ProcessType(process_type) if process_type is not None else None
    logs = Logs(proc_type,
                year,
                month,
                day)
    return [trim_spectre_data_dir_path(log.file_path) for log in logs.log_list]


@log_call
def get_log(
    pid: str
) -> str:
    """Read the contents of a log written by a specific process.

    :param pid: The ID of the process which wrote the file, defaults to None
    :return: The file contents of the log
    """
    logs = Logs()
    log = logs.get_from_pid(pid)
    return log.read()