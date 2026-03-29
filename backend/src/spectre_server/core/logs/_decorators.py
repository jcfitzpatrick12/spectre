# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from typing import Callable, TypeVar, ParamSpec
from functools import wraps

# ParamSpec for capturing the argument types of the function
P = ParamSpec("P")
# TypeVar for capturing the return type of the function
RT = TypeVar("RT")


def log_call(func: Callable[P, RT]) -> Callable[P, RT]:
    """Decorator to log the execution of a function.

    Logs an informational message when the decorated function is called,
    and an error message if the function raises an exception.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> RT:
        logger = logging.getLogger(func.__module__)
        try:
            logger.info(f"Calling the function: {func.__name__}")
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in function: {func.__name__}", exc_info=True)
            raise

    return wrapper
