# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


"""Manage program logging."""

from ._process_types import ProcessType
from ._decorators import log_call
from ._configure import (
    configure_root_logger,
    get_root_logger_state,
    get_server_log_file_path,
    get_worker_log_file_path,
)
from ._logs import Log, Logs

__all__ = [
    "log_call",
    "configure_root_logger",
    "Log",
    "Logs",
    "ProcessType",
    "get_root_logger_state",
    "get_server_log_file_path",
    "get_worker_log_file_path",
]
