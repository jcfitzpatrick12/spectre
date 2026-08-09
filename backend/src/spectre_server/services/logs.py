# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


import spectre_server.core.logs
import spectre_server.core.config


def _get_log(file_name: str) -> spectre_server.core.logs.Log:
    logs = spectre_server.core.logs.Logs(
        spectre_server.core.config.paths.get_logs_dir_path(),
    )
    return logs.get_from_file_name(file_name)


@spectre_server.core.logs.log_call
def get_log(
    file_name: str,
) -> str:
    """Get the file path of a log which exists in the file system.

    :param file_name: Look for any log with this file name.
    :return: The file path of the log if it exists in the file system, as an absolute path within the container's file system.
    """
    log = _get_log(file_name)
    return log.file_path


@spectre_server.core.logs.log_call
def get_log_raw(
    file_name: str,
) -> str:
    """Read a log file.

    :param file_name: The file name of the log.
    :param scope: The process type under which to look for the log.
    :return: The contents of the log, if it exists in the file system.
    """
    log = _get_log(file_name)
    return log.read()


@spectre_server.core.logs.log_call
def delete_log(
    file_name: str,
    dry_run: bool = False,
) -> str:
    """Remove a log from the file system.

    :param file_name: Delete the log with this file name.
    :param scope: The process type under which to look for the log.
    :param dry_run: If True, display which files would be deleted without actually deleting them. Defaults to False
    :return: The file path of the deleted log, as an absolute file path in the container's file system.
    """
    log = _get_log(file_name)
    if not dry_run:
        log.delete()
    return log.file_path


@spectre_server.core.logs.log_call
def get_logs(
    process_types: list[spectre_server.core.logs.ProcessType],
) -> list[str]:
    """Get the file paths of logs which exist in the file system.

    :param process_types: Look for logs under these process types.
    :return: The file paths of all logs under the input tag which exist in the file system, as absolute paths within the container's file system.
    """
    log_paths = []
    for process_type in process_types:
        logs = spectre_server.core.logs.Logs(
            spectre_server.core.config.paths.get_logs_dir_path(process_type.value),
        )
        log_paths += [log.file_path for log in logs]
    return log_paths


@spectre_server.core.logs.log_call
def delete_logs(
    process_types: list[spectre_server.core.logs.ProcessType],
    dry_run: bool = False,
) -> list[str]:
    """Bulk remove logs from the file system.

    Use with caution, the current implementation contains little safeguarding.

    :param process_types: Delete logs under these process types. If none are provided, no logs are deleted.
    :param dry_run: If True, display which files would be deleted without actually deleting them. Defaults to False
    :return: The file paths of logs which have been successfully deleted, as absolute paths within the container's file system.
    """
    deleted_file_paths = []
    for process_type in process_types:
        logs = spectre_server.core.logs.Logs(
            spectre_server.core.config.paths.get_logs_dir_path(process_type.value),
        )
        for log in logs:
            if not dry_run:
                log.delete()
            deleted_file_paths.append(log.file_path)
    return deleted_file_paths
