# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Global dictionaries to hold the mappings
receivers = {}

# classes decorated with @register_receiver("<receiver_name>")
# will be added to the global map of capture_config_mounts with key "receiver_name"
def register_receiver(receiver_name: str):
    def decorator(cls):
        receivers[receiver_name] = cls
        return cls
    return decorator


