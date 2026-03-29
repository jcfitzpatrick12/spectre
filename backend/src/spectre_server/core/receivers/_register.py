# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing

from ._base import Base

# map populated at runtime via the `register_receiver` decorator.
receivers: dict[str, typing.Type[Base]] = {}

T = typing.TypeVar("T", bound=Base)


def register_receiver(
    receiver_name: str,
) -> typing.Callable[[typing.Type[T]], typing.Type[T]]:
    """Decorator to register a fully implemented `Base` subclass under a specified `receiver_name`.

    :param receiver_name: The name of the receiver.
    :raises ValueError: If the provided `receiver_name` is already registered.
    :return: A decorator that registers the `Base` subclass under the given `receiver_name`.
    """

    def decorator(cls: typing.Type[T]) -> typing.Type[T]:
        if receiver_name in receivers:
            raise ValueError(f"The receiver '{receiver_name}' is already registered!")
        receivers[receiver_name] = cls
        return cls

    return decorator


def get_registered_receivers() -> list[str]:
    """List all registered receivers."""
    return [k for k in receivers.keys()]
