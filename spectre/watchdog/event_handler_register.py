# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Global dictionaries to hold the mappings
event_handler_map = {}

# classes decorated with @register_event_handler([EVENT_HANDLER_KEY])
# will be added to event_handler_map
def register_event_handler(event_handler_key: str):
    def decorator(cls):
        event_handler_map[event_handler_key] = cls
        return cls
    return decorator

