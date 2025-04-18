# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import Optional

from spectre_core.logs import ( 
   Logs, Log, ProcessType, log_call, parse_log_base_file_name
)


def _get_log(
    year: int,
    month: int,
    day: int,
    base_file_name: str
) -> Log:
    """Get the `Log` instance corresponding to the input file."""
    _, pid, _ = parse_log_base_file_name(base_file_name)
    logs = Logs(year=year,
                month=month,
                day=day)
    return logs.get_from_pid(pid)


@log_call
def get_log(
    year: int,
    month: int,
    day: int,
    base_file_name: str
) -> str:
    """Get the file path of a log written by a specific process.
    
    :param year: Search for a log file under this numeric year.
    :param month: Search for a log file under this numeric month.
    :param day: Search for a log file under this numeric day.
    :param base_file_name: Search for a log file with this base file name.
    :return: The file path of the log file if it exists in the file system, as an absolute path within the container's file system. 
    """
    log = _get_log(year, month, day, base_file_name) 
    return log.file_path


@log_call
def get_log_raw(
    year: int,
    month: int,
    day: int,
    base_file_name: str
) -> str:
    """Read the log written by a specific process.

    :param year: Read a log file under this numeric year.
    :param month: Read a log file under this numeric month.
    :param day: Read a log file under this numeric day.
    :base_file_name: Read the log file with this base file name.
    :return: The contents of the log, if it exists in the file system.
    """
    log = _get_log(year, month, day, base_file_name)
    return log.read()


@log_call
def get_logs(
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    process_types: list[str] = [],
) -> list[str]:
    """Get the file paths of logs which exist in the file system.

    :param process_types: Filter logs by their process type, defaults to None
    :param year: Filter logs by the numeric year, defaults to None
    :param month: Filter logs by the numeric month, defaults to None
    :param day: Filter logs by the numeric day, defaults to None
    :return: The file paths of logs which exist in the file system, as absolute paths within the container's file system.
    """
    if not process_types:
        process_types = ["user", "worker"]
   
   
    log_file_paths = []
    for process_type in process_types:
        proc_type = ProcessType(process_type) 
        logs = Logs(proc_type,
                    year,
                    month,
                    day)
        log_file_paths += [log.file_path for log in logs.log_list]
        
    return log_file_paths


@log_call
def delete_log(
    year: int,
    month: int,
    day: int,
    base_file_name: str
) -> str:
    """Delete a log in the file system.

    :param year: Delete a log under this numeric year.
    :param month: Delete a log under this numeric month.
    :param day: Delete a log under this numeric day.
    :param base_file_name: Delete a batch file with this file name.
    :return: The file path of the deleted log file, as an absolute path in the container's file system.
    """
    log = _get_log(year, month, day, base_file_name)
    log.delete()
    _LOGGER.info(f"Log deleted: {log.file_path}")
    return log.file_path


@log_call
def delete_logs(
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    process_types: list[str] = [],
) -> list[str]:
    """Delete log files. Use with caution, the current implementation contains little safeguarding.

    :param process_type: Only delete logs with a particular process type. If no process type is given,
    then log files with any process type will be deleted. Defaults to None
    :param year: Delete only log files from this numeric year. Defaults to None. If no year, month, 
    or day is specified, files from any year will be deleted.
    :param month: Delete only log files from this numeric month. Defaults to None. If a year is 
    specified but not a month, all files from that year will be deleted.
    :param day: Delete only log files from this numeric day. Defaults to None. If both year and month 
    are specified but not a day, all files from that year and month will be deleted.
    :return: The file paths of all logs which were deleted, as absolute paths within the container's file system.
    """
    deleted_file_paths = []
    for process_type in process_types:
        proc_type = ProcessType(process_type)
        logs = Logs(proc_type,
                    year,
                    month,
                    day)
        for log in logs:
            # if process type is specified, disregard all logs of differing process types
            if process_type and log.process_type != process_type:
                continue
            log.delete()
            _LOGGER.info(f"File deleted: {log.file_path}")
            deleted_file_paths.append(log.file_path)

    return deleted_file_paths














