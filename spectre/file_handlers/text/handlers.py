# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from datetime import datetime

from spectre.file_handlers.base import BaseFileHandler
from spectre.cfg import (
    LOGS_DIR_PATH, 
    DEFAULT_DATETIME_FORMAT,
    DEFAULT_TIME_FORMAT
)

class TextHandler(BaseFileHandler):
    def __init__(self, parent_path: str, base_file_name: str, **kwargs):
        super().__init__(parent_path, base_file_name, extension = "txt", **kwargs)
        return 
    
    def _read(self) -> dict:
        with open(self.file_path, 'r') as f:
            return f.read()
        

# logs will be created under LOGS_DIR_PATH/yyyy/mm/dd/%Y-%m-%dT%H:%M:%S_pid.logs
class LogsHandler(TextHandler):

    PROCESS_TYPES = [
        "USER",
        "WORKER"
    ]
    
    def __init__(self, 
                 datetime_stamp: str, # system datetime at log creation
                 pid: str, # process id
                 process_type: str, # process type
                 ):
        
        if process_type not in self.PROCESS_TYPES:
            raise ValueError(f"Invalid process type: {process_type}. Expected one of {self.PROCESS_TYPES}")

        datetime_stamp = datetime.strptime(datetime_stamp, DEFAULT_DATETIME_FORMAT)
        # Build the date directory path using os.path.join
        date_dir = os.path.join(
            datetime_stamp.strftime("%Y"),
            datetime_stamp.strftime("%m"),
            datetime_stamp.strftime("%d")
        )
        parent_path = os.path.join(LOGS_DIR_PATH, date_dir)

        time_stamp = datetime_stamp.strftime(DEFAULT_TIME_FORMAT)
        base_file_name = f"{time_stamp}_{pid}_{process_type}"
        super().__init__(parent_path, base_file_name, override_extension = "logs")
    
