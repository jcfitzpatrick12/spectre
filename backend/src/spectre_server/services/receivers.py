# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any

from spectre_core.logs import log_call
from spectre_core.receivers import get_receiver, get_registered_receivers, ReceiverName

@log_call
def get_receiver_names(
) -> list[str]:
    """List the names of all registered receiver supported by `spectre`."""
    return get_registered_receivers()
    

@log_call
def get_modes(
    receiver_name: str,
) -> list[str]:
    """Get the defined operating modes for the input receiver.

    :param receiver_name: The name of the receiver.
    :return: All the defined operating modes for the receiver.
    """
    receiver = get_receiver( ReceiverName(receiver_name) )
    return receiver.modes


@log_call
def get_specs(
    receiver_name: str,
) -> dict[str, float|int|list[float|int]]:
    """Get the hardware specifications for the input receiver.

    :param receiver_name: The name of the receiver.
    :return: The hardware specifications for the receiver.
    """
    receiver = get_receiver( ReceiverName(receiver_name) )
    return {k.value: v for k,v in receiver.specs.items()}


@log_call
def get_capture_template(
    receiver_name: str,
    receiver_mode: str
) -> dict[str, Any]:
    """Get the capture template for a receiver in a particular operating mode.

    :param receiver_name: The name of the receiver.
    :param receiver_mode: The operating mode for the receiver.
    :return: The capture template converted to a serialisable dictionary.
    """
    name = ReceiverName(receiver_name)
    receiver = get_receiver(name, 
                            mode = receiver_mode)
    
    return receiver.capture_template.to_dict()
