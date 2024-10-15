# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from collections import OrderedDict
import logging
import os
from datetime import datetime
from os import walk
from os.path import splitext
import warnings

from spectre.file_handlers.text.handlers import TextHandler
from spectre.cfg import get_logs_dir_path
from spectre.cfg import (
    LOGS_DIR_PATH, 
    DEFAULT_DATETIME_FORMAT,
    DEFAULT_TIME_FORMAT
)

PROCESS_TYPES = [
        "USER",
        "WORKER"
    ]


def validate_process_type(process_type: str) -> None:
    if process_type not in PROCESS_TYPES:
        error_message = f"Invalid process type: {process_type}. Expected one of {PROCESS_TYPES}"
        _LOGGER.error(error_message, exc_info=True)
        raise ValueError(error_message)


class LogHandler(TextHandler): 
    def __init__(self, 
                 datetime_stamp: str, # system datetime at log creation
                 pid: str, # process id
                 process_type: str, # process type
                 ):
        
        self.datetime_stamp: str = datetime_stamp
        self.pid: str = pid
        self.process_type: str = process_type

        validate_process_type(process_type)

        dt = datetime.strptime(datetime_stamp, DEFAULT_DATETIME_FORMAT)
        # Build the date directory path using os.path.join
        date_dir = os.path.join(
            dt.strftime("%Y"),
            dt.strftime("%m"),
            dt.strftime("%d")
        )
        parent_path = os.path.join(LOGS_DIR_PATH, date_dir)

        base_file_name = f"{datetime_stamp}_{pid}_{process_type}"
        super().__init__(parent_path, base_file_name, override_extension = "log")
    

def configure_root_logger(process_type: str, 
                          level: int = logging.INFO) -> LogHandler:
    system_datetime = datetime.now()
    datetime_stamp = system_datetime.strftime(DEFAULT_DATETIME_FORMAT)
    log_handler = LogHandler(datetime_stamp, 
                               os.getpid(), 
                               process_type)
    log_handler.make_parent_path()

    # Configure the root logger
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
        level=level,
        datefmt=DEFAULT_DATETIME_FORMAT, 
        filename=log_handler.file_path
    )

    _LOGGER.info("Logging successfully configured.")
    return log_handler


class LogHandlers:
    def __init__(self, 
                 process_type: str | None = None,
                 year: int = None, 
                 month: int = None, 
                 day: int = None):
        _LOGGER.info(f"Initialising logs with process type: {process_type if process_type else 'not specified'}")
        self.process_type: str | None = process_type
        self.year: int | None = year
        self.month: int | None = month
        self.day: int | None = day

        if self.process_type:
            validate_process_type(process_type)

        # set the directory which holds the chunks (by default, we use the entire chunks directory)
        self.logs_dir_path = get_logs_dir_path(year, month, day)

        self._set_log_handler_map()

        # internal attribute to assist in making Chunks iterable
        self._current_index = 0


    def _set_log_handler_map(self) -> None:
        log_handler_map = OrderedDict()
        log_files = [f for (_, _, files) in walk(self.logs_dir_path) for f in files]

        if not log_files:
            warning_message = "No logs found, setting log map to an empty dictionary."
            _LOGGER.warning(warning_message)
            warnings.warn(warning_message)
            self.log_handler_map = log_handler_map
            return

        for log_file in log_files:
            # strip the extension
            file_name, _ = splitext(log_file)
            # split the file name into its components
            log_start_time, pid, process_type = file_name.split("_")
            # if the user has defined a particular process type, skip the file if not applicable
            if self.process_type and process_type != self.process_type:
                continue
            # map the file name to the corresponding log handler
            log_handler_map[file_name] = LogHandler(log_start_time, pid, process_type)

        # sort log handlers in ascending order according to date
        self.log_handler_map = OrderedDict(sorted(log_handler_map.items()))
        # set the list of log handlers 
        self._log_handler_list: list[LogHandler] = self.get_log_handler_list()

    
    # an alias for _set_log_handler_map()
    def update_chunk_map(self) -> None:
        _LOGGER("Updating the log handler map.")
        self._set_log_handler_map()
        return
    
    
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
        _LOGGER.info("Getting the list of log handlers")
        return list(self.log_handler_map.values())
    

    def get_log_file_name_list(self) -> list[str]:
        _LOGGER.info("Getting the list of log file names")
        return list(self.log_handler_map.keys())
    

    def get_log_handler_from_file_name(self, file_name: str) -> LogHandler:
        try:
            return self.log_handler_map[file_name]
        except KeyError:
            error_message = f"Log handler for file name '{file_name}' not found in log map."
            _LOGGER.error(error_message)
            raise KeyError(error_message)


    def get_log_handler_from_pid(self, pid: str) -> LogHandler:
        for log_handler in self._log_handler_list:
            if log_handler.pid == pid:
                return log_handler
        error_message = f"Log handler for PID '{pid}' not found in log map."
        _LOGGER.error(error_message)
        raise KeyError(error_message)



