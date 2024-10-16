# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.watchdog.event_handler_register import event_handler_map
from spectre.file_handlers.json.handlers import CaptureConfigHandler

def get_event_handler(event_handler_key: str):
    # try and fetch the capture config mount
    event_handler = event_handler_map.get(event_handler_key)
    if event_handler is None:
        valid_event_handler_keys = list(event_handler_map.keys())
        raise ValueError(f"No chunk found for the event handler key: {event_handler_key}. Please specify one of the following event handler keys {valid_event_handler_keys}")
    return event_handler

def get_event_handler_from_tag(tag: str):
    capture_config_handler = CaptureConfigHandler(tag)
    capture_config = capture_config_handler.read()
    event_handler_key = capture_config.get('event_handler_key', None)
    return get_event_handler(event_handler_key)
