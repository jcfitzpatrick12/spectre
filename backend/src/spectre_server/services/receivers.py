# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any

from spectre_core.logging import log_call
from spectre_core.receivers.factory import get_receiver
from spectre_core.receivers.receiver_register import list_all_receiver_names


@log_call
def get_receiver_names(
) -> list[str]:
    """Get all defined receiver names"""
    return list_all_receiver_names()


@log_call
def get_modes(receiver_name: str,
) -> list[str]:
    """For the input receiver, get all the defined modes"""
    receiver = get_receiver(receiver_name)
    return receiver.valid_modes


@log_call
def get_specifications(receiver_name: str,
) -> dict[str, Any]:
    """For the input receiver, get the corresponding specifications"""
    receiver = get_receiver(receiver_name)
    return receiver.specifications