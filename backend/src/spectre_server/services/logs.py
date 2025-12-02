# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path

import spectre_core.logs
import spectre_core.config


def _get_log(
    file_name: str,
) -> spectre_core.logs.Log:
    start_time, pid, process_type = spectre_core.logs.parse_log_file_name(file_name)
    dt = datetime.strptime(start_time, spectre_core.config.TimeFormat.DATETIME)
    logs = spectre_core.logs.Logs(
        process_type,
        spectre_core.config.paths.get_logs_dir_path(dt.year, dt.month, dt.day),
    )
    return logs.get_from_pid(pid)


@spectre_core.logs.log_call
def get_log(
    file_name: str,
) -> str:
    """Get the file path of a log which exists in the file system.

    :param file_name: Look for any log with this file name.
    :return: The file path of the log if it exists in the file system, as an absolute path within the container's file system.
    """
    log = _get_log(file_name)
    return log.file_path


@spectre_core.logs.log_call
def get_log_raw(
    file_name: str,
) -> str:
    """Read a log file.

    :param file_name: The file name of the log.
    :return: The contents of the log, if it exists in the file system.
    """
    log = _get_log(file_name)
    return log.read()


@spectre_core.logs.log_call
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
        logs = spectre_core.logs.Logs(
            spectre_core.logs.ProcessType(process_type).value,
            spectre_core.config.paths.get_logs_dir_path(year, month, day),
        )
        log_file_paths += [log.file_path for log in logs]

    return log_file_paths


@spectre_core.logs.log_call
def delete_log(
    file_name: str,
    dry_run: bool = False,
) -> str:
    """Remove a log from the file system.

    :param file_name: Delete the log with this file name.
    :param dry_run: If True, display which files would be deleted without actually deleting them. Defaults to False
    :return: The file path of the deleted log, as an absolute file path in the container's file system.
    """
    log = _get_log(file_name)
    if not dry_run:
        log.delete()
    return log.file_path


@spectre_core.logs.log_call
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
        proc_type = spectre_core.logs.ProcessType(process_type).value
        logs = spectre_core.logs.Logs(
            proc_type, spectre_core.config.paths.get_logs_dir_path(year, month, day)
        )
        for log in logs:
            if not dry_run:
                log.delete()
            deleted_file_paths.append(log.file_path)

    return deleted_file_paths


@spectre_core.logs.log_call
def prune_logs_older_than(days: int, dry_run: bool = False) -> list[str]:
    """Delete logs older than the requested age."""

    if days < 0:
        raise ValueError("days must be greater than or equal to zero")

    cutoff_timestamp = (datetime.utcnow() - timedelta(days=days)).timestamp()
    deleted_file_paths: list[str] = []

    for file_path in get_logs([], None, None, None):
        path_obj = Path(file_path)
        try:
            file_mtime = path_obj.stat().st_mtime
        except FileNotFoundError:
            continue

        if file_mtime <= cutoff_timestamp:
            if not dry_run:
                try:
                    path_obj.unlink()
                except FileNotFoundError:
                    continue
            deleted_file_paths.append(file_path)

    return deleted_file_paths
