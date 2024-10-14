# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

import logging
import os
from datetime import datetime

from spectre.file_handlers.text.handlers import LogsHandler
from spectre.cfg import DEFAULT_DATETIME_FORMAT

def configure_root_logger(process_type: str, 
                          level: int = logging.INFO) -> None:
    system_datetime = datetime.now()
    datetime_stamp = system_datetime.strftime(DEFAULT_DATETIME_FORMAT)
    logs_handler = LogsHandler(datetime_stamp, 
                               os.getpid(), 
                               process_type)
    logs_handler.make_parent_path()

    # Configure the root logger
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
        level=level,
        datefmt=DEFAULT_DATETIME_FORMAT, 
        filename=logs_handler.file_path
    )

    _LOGGER.info("Logging successfully configured.")
