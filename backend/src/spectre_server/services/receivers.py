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
    return receiver.modes


@log_call
def get_specs(receiver_name: str,
) -> dict[str, Any]:
    """For the input receiver, get the corresponding specifications"""
    receiver = get_receiver(receiver_name)
    return receiver.specs.to_dict()


@log_call
def get_capture_template(receiver_name: str,
                      mode: str
) -> dict[str, Any]:
    """Get the type template for a capture config for a receiver operating in a particular mode.
    
    Optionally, format the return as a command to create a capture config with the input tag.
    """
    receiver = get_receiver(receiver_name, 
                            mode = mode)
    
    return receiver.capture_template.to_dict()