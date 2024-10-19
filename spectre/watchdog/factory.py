# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.watchdog.event_handler_register import event_handler_map
from spectre.file_handlers.json import CaptureConfigHandler
from spectre.exceptions import EventHandlerNotFound

def get_event_handler(event_handler_key: str):
    # try and fetch the capture config mount
    try:
        return event_handler_map[event_handler_key]
    except KeyError:
        valid_event_handler_keys = list(event_handler_map.keys())
        raise EventHandlerNotFound(f"No event handler found for the event handler key: {event_handler_key}. Please specify one of the following event handler keys {valid_event_handler_keys}")

def get_event_handler_from_tag(tag: str):
    capture_config_handler = CaptureConfigHandler(tag)
    capture_config = capture_config_handler.read()
    event_handler_key = capture_config.get('event_handler_key')
    return get_event_handler(event_handler_key)
