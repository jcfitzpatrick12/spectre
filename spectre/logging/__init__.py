# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Callable
import logging
import os
import warnings
from collections import OrderedDict
from datetime import datetime
from logging import getLogger
from os import walk
from os.path import splitext

from spectre.cfg import (
    LOGS_DIR_PATH, 
    DEFAULT_DATETIME_FORMAT, 
    get_logs_dir_path
)
from spectre.file_handlers.text import TextHandler
from spectre.exceptions import LogNotFoundError

_LOGGER = getLogger(__name__)

PROCESS_TYPES = ["USER", "WORKER"]

def validate_process_type(process_type: str) -> None:
    if process_type not in PROCESS_TYPES:
        raise ValueError(f"Invalid process type: {process_type}. Expected one of {PROCESS_TYPES}")


class LogHandler(TextHandler):
    def __init__(self, datetime_stamp: str, pid: str, process_type: str):
        self.datetime_stamp = datetime_stamp
        self.pid = pid
        self.process_type = process_type

        validate_process_type(process_type)

        dt = datetime.strptime(datetime_stamp, DEFAULT_DATETIME_FORMAT)
        date_dir = os.path.join(dt.strftime("%Y"), dt.strftime("%m"), dt.strftime("%d"))
        parent_path = os.path.join(LOGS_DIR_PATH, date_dir)
        base_file_name = f"{datetime_stamp}_{pid}_{process_type}"

        super().__init__(parent_path, base_file_name, override_extension="log")


class LogHandlers:
    def __init__(self, process_type: str | None = None, year: int = None, month: int = None, day: int = None):
        self.process_type = process_type
        self.year = year
        self.month = month
        self.day = day

        if self.process_type:
            validate_process_type(process_type)


        self.logs_dir_path = get_logs_dir_path(year, month, day)
        self._set_log_handler_map()
        self._current_index = 0


    def _set_log_handler_map(self) -> None:
        log_handler_map = OrderedDict()
        log_files = [f for (_, _, files) in walk(self.logs_dir_path) for f in files]

        if not log_files:
            warning_message = "No logs found, setting log map to an empty dictionary."
            _LOGGER.warning(warning_message)
            warnings.warn(warning_message)
            self.log_handler_map = log_handler_map
            self._log_handler_list = self.get_log_handler_list()
            return

        for log_file in log_files:
            file_name, _ = splitext(log_file)
            log_start_time, pid, process_type = file_name.split("_")

            if self.process_type and process_type != self.process_type:
                continue

            log_handler_map[file_name] = LogHandler(log_start_time, pid, process_type)

        self.log_handler_map = OrderedDict(sorted(log_handler_map.items()))
        self._log_handler_list = self.get_log_handler_list()


    def update_chunk_map(self) -> None:
        self._set_log_handler_map()


    def __iter__(self):
        self._current_index = 0
        return self


    def __next__(self) -> LogHandler:
        if self._current_index < len(self._log_handler_list):
            log_handler = self._log_handler_list[self._current_index]
            self._current_index += 1
            return log_handler
        else:
            raise StopIteration


    def get_log_handler_list(self) -> list[LogHandler]:
        return list(self.log_handler_map.values())


    def get_log_file_name_list(self) -> list[str]:
        return list(self.log_handler_map.keys())


    def get_log_handler_from_file_name(self, file_name: str) -> LogHandler:
        # auto strip the extension if present
        file_name, _ = os.path.splitext(file_name)
        try:
            return self.log_handler_map[file_name]
        except KeyError:
            raise LogNotFoundError(f"Log handler for file name '{file_name}' not found in log map")


    def get_log_handler_from_pid(self, pid: str) -> LogHandler:
        for log_handler in self._log_handler_list:
            if log_handler.pid == pid:
                return log_handler
        raise LogNotFoundError(f"Log handler for PID '{pid}' not found in log map")


def configure_root_logger(process_type: str, 
                          level: int = logging.INFO) -> LogHandler:
    system_datetime = datetime.now()
    datetime_stamp = system_datetime.strftime(DEFAULT_DATETIME_FORMAT)
    pid = os.getpid()
    log_handler = LogHandler(datetime_stamp, pid, process_type)
    log_handler.make_parent_path()

    # configure the root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    # Remove any existing handlers to avoid duplicate logs
    for handler in logger.handlers:
        logger.removeHandler(handler)
    # Set up file handler with specific filename
    file_handler = logging.FileHandler(log_handler.file_path)
    file_handler.setLevel(level)
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)8s] --- %(message)s (%(name)s:%(lineno)s)")
    file_handler.setFormatter(formatter)
    # and add it to the root logger
    logger.addHandler(file_handler)

    return log_handler

# Logger must be passed in to preserve context of the service function
def log_service_call(logger: logging.Logger) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                logger.info(f"Calling the service function: {func.__name__}")
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"An error occurred while calling the service function: {func.__name__}",
                              exc_info=True)
                raise
        return wrapper
    return decorator