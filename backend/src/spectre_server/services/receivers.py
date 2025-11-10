# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing

import spectre_core.logs
import spectre_core.receivers


@spectre_core.logs.log_call
def get_receiver_names() -> list[str]:
    """List the names of all supported receivers."""
    return spectre_core.receivers.get_registered_receivers()


@spectre_core.logs.log_call
def get_modes(
    receiver_name: str,
) -> list[str]:
    """Get the defined operating modes for a receiver.

    :param receiver_name: The name of the receiver.
    :return: The operating modes for the receiver.
    """
    receiver = spectre_core.receivers.get_receiver(receiver_name)
    return receiver.modes


@spectre_core.logs.log_call
def get_model(receiver_name: str, receiver_mode: str) -> dict[str, typing.Any]:
    """Get the model for a receiver in a particular operating mode.

    :param receiver_name: The name of the receiver.
    :param receiver_mode: The operating mode for the receiver.
    :return: The serialisable model.
    """
    receiver = spectre_core.receivers.get_receiver(receiver_name, receiver_mode)
    return receiver.model_schema
