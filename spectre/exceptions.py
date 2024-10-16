# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from typing import Callable

class ChunkNotFoundError(Exception): ...
class ChunkFileNotFoundError(FileNotFoundError): ...
class InvalidMetadataError(Exception): ...
class InvalidSweepMetadataError(InvalidMetadataError): ...
class InvalidTagError(ValueError): ...
class SpectrogramNotFoundError(FileNotFoundError): ...
class LogNotFoundError(FileNotFoundError): ...
class ReceiverNotFoundError(Exception): ...
class InvalidReceiver(Exception): ...
class InvalidModeError(Exception): ...


def log_exceptions(logger: logging.Logger) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error("An error occurred in function %s: %s", func.__name__, e, exc_info=True)
                raise
        return wrapper
    return decorator

