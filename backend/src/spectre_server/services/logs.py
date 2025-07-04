# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from typing import Optional
from datetime import datetime

from spectre_core.logs import Logs, Log, ProcessType, log_call, parse_log_file_name
from spectre_core.config import TimeFormat


def _get_log(
    file_name: str,
) -> Log:
    """Get the `Log` instance corresponding to the input file."""
    start_time, pid, process_type = parse_log_file_name(file_name)
    dt = datetime.strptime(start_time, TimeFormat.DATETIME)
    logs = Logs(
        process_type=ProcessType(process_type), year=dt.year, month=dt.month, day=dt.day
    )
    return logs.get_from_pid(pid)


@log_call
def get_log(
    file_name: str,
) -> str:
    """Get the file path of a log which exists in the file system.

    :param file_name: Look for any log with this file name.
    :return: The file path of the log if it exists in the file system, as an absolute path within the container's file system.
    """
    log = _get_log(file_name)
    return log.file_path


@log_call
def get_log_raw(
    file_name: str,
) -> str:
    """Read a log file.

    :param file_name: The file name of the log.
    :return: The contents of the log, if it exists in the file system.
    """
    log = _get_log(file_name)
    return log.read()


@log_call
def get_logs(
    process_types: list[str],
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> list[str]:
    """Get the file paths of logs which exist in the file system.

    :param process_types: Look for logs with these process types. If none are specified, look for logs with any process type.
    :param year: Only look for logs under this year, defaults to None. If year, month and day are unspecified, look for logs under any year.
    :param month: Only look for logs under this month, defaults to None. If year is specified, but not month and day, look for logs under that year.
    :param day: Only look for logs under this day, defaults to None. If year and month are specified, but not day, look for logs under that month and year.
    :return: The file paths of all logs under the input tag which exist in the file system, as absolute paths within the container's file system.
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
    dry_run: bool = False,
) -> str:
    """Remove a log from the file system.

    :param file_name: Delete the log with this file name.
    :param year: Delete a log under this year. Defaults to None.
    :param month: Delete a log under this month. Defaults to None.
    :param day: Delete a log under this day. Defaults to None.
    :param dry_run: If True, display which files would be deleted without actually deleting them. Defaults to False
    :return: The file path of the deleted log, as an absolute file path in the container's file system.
    """
    log = _get_log(file_name)
    if not dry_run:
        log.delete()
    return log.file_path


@log_call
def delete_logs(
    process_types: list[str],
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    dry_run: bool = False,
) -> list[str]:
    """Bulk remove logs from the file system.

    Use with caution, the current implementation contains little safeguarding.

    :param process_types: Delete logs with these process types. If none are provided, no logs are deleted.
    :param year: Only delete logs under this year. Defaults to None. If no year, month, or day is specified, files from any year will be deleted.
    :param month: Only delete logs under this month. Defaults to None. If a year is specified, but not a month, all files from that year will be deleted.
    :param day: Only delete logs under this day. Defaults to None. If both year and month are specified, but not the day, all files from that year and month will be deleted.
    :param dry_run: If True, display which files would be deleted without actually deleting them. Defaults to False
    :return: The file paths of logs which have been successfully deleted, as absolute paths within the container's file system.
    """
    deleted_file_paths = []
    for process_type in process_types:
        proc_type = ProcessType(process_type)
        logs = Logs(proc_type, year, month, day)
        for log in logs:
            if not dry_run:
                log.delete()
            deleted_file_paths.append(log.file_path)

    return deleted_file_paths
