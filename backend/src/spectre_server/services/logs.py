# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from typing import Optional

from spectre_core.logs import Logs, Log, ProcessType, log_call, parse_log_file_name


def _get_log(
    file_name: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> Log:
    """Get the `Log` instance corresponding to the input file."""
    _, pid, process_type = parse_log_file_name(file_name)
    logs = Logs(process_type=ProcessType(process_type), year=year, month=month, day=day)
    return logs.get_from_pid(pid)


@log_call
def get_log(
    file_name: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> str:
    """Get the file path of a log written by a specific process.

    :param file_name: Look for a log file with this file name.
    :param year: Look for a log file under this numeric year. Defaults to None.
    :param month: Look for a log file under this numeric month. Defaults to None.
    :param day: Look for a log file under this numeric day. Defaults to None.
    :return: The file path of the log file if it exists in the file system, as an absolute path within the container's file system.
    """
    log = _get_log(file_name, year, month, day)
    return log.file_path


@log_call
def get_log_raw(
    file_name: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> str:
    """Read the log written by a specific process.

    :param file_name: Read the log file with this file name.
    :param year: Read a log file under this numeric year.
    :param month: Read a log file under this numeric month.
    :param day: Read a log file under this numeric day.
    :return: The contents of the log, if it exists in the file system.
    """
    log = _get_log(file_name, year, month, day)
    return log.read()


@log_call
def get_logs(
    process_types: list[str],
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> list[str]:
    """Get the file paths of logs which exist in the file system.

    :param process_types: Filter logs by their process type. If no process types are specified, consider all process types.
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
        logs = Logs(proc_type, year, month, day)
        log_file_paths += [log.file_path for log in logs.log_list]

    return log_file_paths


@log_call
def delete_log(
    file_name: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> str:
    """Delete a log in the file system.

    :param file_name: Delete a batch file with this file name.
    :param year: Delete a log under this numeric year. Defaults to None.
    :param month: Delete a log under this numeric month. Defaults to None.
    :param day: Delete a log under this numeric day. Defaults to None.
    :return: The file path of the deleted log file, as an absolute path in the container's file system.
    """
    log = _get_log(file_name, year, month, day)
    log.delete()
    return log.file_path


@log_call
def delete_logs(
    process_types: list[str],
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> list[str]:
    """Delete log files. Use with caution, the current implementation contains little safeguarding.

    :param process_types: Delete logs with these process types. If no process type is given, then no logs will be deleted.
    :param year: Delete only log files from this numeric year. Defaults to None. If no year, month,  or day is specified,
    files from any year will be deleted.
    :param month: Delete only log files from this numeric month. Defaults to None. If a year is  specified but not a month,
    all files from that year will be deleted.
    :param day: Delete only log files from this numeric day. Defaults to None. If both year and month  are specified but not
    a day, all files from that year and month will be deleted.
    :return: The file paths of all logs which were deleted, as absolute paths within the container's file system.
    """
    deleted_file_paths = []
    for process_type in process_types:
        proc_type = ProcessType(process_type)
        logs = Logs(proc_type, year, month, day)
        for log in logs:
            log.delete()
            deleted_file_paths.append(log.file_path)

    return deleted_file_paths
