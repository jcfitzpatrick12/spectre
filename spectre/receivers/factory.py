# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from spectre.receivers.receiver_register import receivers
from spectre.receivers.base import BaseReceiver
from spectre.exceptions import ReceiverNotFoundError

# used to fetch an instance of the receiver class
def get_receiver(receiver_name: str, mode: str = None) -> BaseReceiver:
    info_message = f"Getting an instance of a receiver with name {receiver_name} {' in mode: ' + mode if mode else 'no mode specified'}"
    _LOGGER.info(info_message)
    # try and fetch the capture config mount
    try:
        Receiver = receivers[receiver_name]
    except KeyError:
        valid_receivers = list(receivers.keys())
        raise ReceiverNotFoundError(f"No class found for the receiver: {receiver_name}. Please specify one of the following receivers {valid_receivers}.")
    
    # return an instance of the receiver
    return Receiver(receiver_name, mode = mode)