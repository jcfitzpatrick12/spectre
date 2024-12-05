# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any, Optional
from enum import Enum

from spectre_core.logging import log_call
from spectre_core.receivers.factory import get_receiver
from spectre_core.receivers.receiver_register import list_all_receiver_names

class QueryFor(Enum):
    MODES = "modes"
    SPECIFICATIONS = "specifications"
    TYPE_TEMPLATE = "type-template"


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


@log_call
def get_type_template(receiver_name: str,
                      mode: str
) -> dict[str, Any]:
    """Get the type template for a capture config for a receiver operating in a particular mode.
    
    Optionally, format the return as a command to create a capture config with the input tag.
    """
    receiver = get_receiver(receiver_name, 
                            mode = mode)
    
    return {k: v.__name__ for k, v in receiver.type_template.items()}


@log_call
def query_for(receiver_name: str,
              query: str,
              mode: Optional[str] = None,
) -> Any:
    
    if query == QueryFor.MODES.value:
        return get_modes(receiver_name)
    
    if query == QueryFor.SPECIFICATIONS.value:
        return get_specifications(receiver_name)
    
    elif query == QueryFor.TYPE_TEMPLATE.value:
        # mode specific queries
        if mode is None:
            raise ValueError(f"Mode is required for querying type template")
        return get_type_template(receiver_name, 
                                 mode)
    
    raise ValueError(f"Unsupported query type: {query}")