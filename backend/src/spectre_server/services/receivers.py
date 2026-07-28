# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
import typing

import spectre_server.core.logs
import spectre_server.core.receivers


@spectre_server.core.logs.log_call
def get_receivers() -> list[str]:
    """List the names of all supported receivers."""
    return spectre_server.core.receivers.get_registered_receivers()


@spectre_server.core.logs.log_call
def discover_receiver(receiver_name: str) -> dict[str, typing.Any]:
    """Return receiver metadata and whether the receiver can be discovered."""
    receiver = spectre_server.core.receivers.get_receiver(receiver_name)
    try:
        result = subprocess.run(
            receiver.discovery_command, capture_output=True, check=False
        )
        found = result.returncode == 0
    except FileNotFoundError:
        found = False
    return {"name": receiver.name, "modes": receiver.modes, "found": found}


@spectre_server.core.logs.log_call
def get_modes(
    receiver_name: str,
) -> list[str]:
    """Get the defined operating modes for a receiver.

    :param receiver_name: The name of the receiver.
    :return: The operating modes for the receiver.
    """
    receiver = spectre_server.core.receivers.get_receiver(receiver_name)
    return receiver.modes


@spectre_server.core.logs.log_call
def get_model(receiver_name: str, receiver_mode: str) -> dict[str, typing.Any]:
    """Get the model for a receiver in a particular operating mode.

    :param receiver_name: The name of the receiver.
    :param receiver_mode: The operating mode for the receiver.
    :return: The serialisable model.
    """
    receiver = spectre_server.core.receivers.get_receiver(receiver_name, receiver_mode)
    return receiver.model_schema
