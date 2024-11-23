# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional

from spectre.receivers.receiver_register import receivers
from spectre.receivers.base import BaseReceiver
from spectre.exceptions import ReceiverNotFoundError

# used to fetch an instance of the receiver class
def get_receiver(receiver_name: str, mode: Optional[str] = None) -> BaseReceiver:
    Receiver = receivers.get(receiver_name)
    if Receiver is None:
        valid_receivers = list(receivers.keys())
        raise ReceiverNotFoundError(f"No class found for the receiver: {receiver_name}. "
                                    f"Please specify one of the following receivers {valid_receivers}")
    return Receiver(receiver_name, 
                    mode = mode)
