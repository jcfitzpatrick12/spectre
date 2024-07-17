# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# it is important to import the receivers library
# since the decorators only take effect on import
# this import will run the __init__.py within library, which will dynamically import all the receivers
import spectre.receivers.library

from spectre.receivers.BaseReceiver import BaseReceiver

# Global dictionaries to hold the mappings
receivers = {}

# classes decorated with @register_receiver("<receiver_name>")
# will be added to the global map of capture_config_mounts with key "receiver_name"
def register_receiver(receiver_name: str):
    def decorator(cls):
        receivers[receiver_name] = cls
        return cls
    return decorator


# fetch a capture mount for a given receiver name
def get_receiver(receiver_name: str, mode: str) -> BaseReceiver:
    # try and fetch the capture config mount
    Receiver = receivers.get(receiver_name)
    if Receiver is None:
        valid_receivers = list(receivers.keys())
        raise ValueError(f"No capture mount found for receiver: {receiver_name}. Please specify one of the following receivers {valid_receivers}.")
    
    # return an instance of the receiver
    return Receiver(receiver_name, mode)


