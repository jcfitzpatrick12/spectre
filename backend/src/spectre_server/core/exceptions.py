# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Spectre custom exceptions.
"""

import warnings
from functools import wraps
from typing import TypeVar, Callable, Any, cast

F = TypeVar("F", bound=Callable[..., Any])


def deprecated(message: str) -> Callable[[F], F]:
    """A decorator to mark functions as deprecated.

    :param message: Warning message explaining what to use instead
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(
                f"{func.__name__} is deprecated. {message}",
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator


class ModeNotFoundError(KeyError): ...


class ReceiverNotFoundError(KeyError): ...


class InvalidSweepMetadataError(ValueError): ...
