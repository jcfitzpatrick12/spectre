# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# it is important to import the receivers library
# since the decorators only take effect on import
# this import will run the __init__.py within library, which will dynamically import all the receivers
import spectre.receivers.library
from spectre.receivers.receiver_register import receivers
from spectre.receivers.BaseReceiver import BaseReceiver

# used to fetch an instance of the receiver class
def get_receiver(receiver_name: str, mode: str) -> BaseReceiver:
    # try and fetch the capture config mount
    Receiver = receivers.get(receiver_name)
    if Receiver is None:
        valid_receivers = list(receivers.keys())
        raise ValueError(f"No capture mount found for receiver: {receiver_name}. Please specify one of the following receivers {valid_receivers}.")
    
    # return an instance of the receiver
    return Receiver(receiver_name, mode)