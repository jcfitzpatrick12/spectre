# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import importlib
import pkgutil 

library_path = os.path.dirname(__file__)

def import_event_handler(event_handler_key: str):
    # create the full path to the event handler
    event_handler_path = os.path.join(library_path, event_handler_key)
    # ensure this path describes a directory, not a file
    if not os.path.isdir(event_handler_path):
        return

    # list all subdirectories
    dir_contents = [d for d in os.listdir(event_handler_path) if not d == "__pycache__"]


    if "EventHandler.py" not in dir_contents:
        return
    
    full_module_name = f'spectre.watchdog.library.{event_handler_key}.EventHandler'

    importlib.import_module(full_module_name)


# list all directories which are not __pycache__
event_handler_keys = [subdir for subdir in os.listdir(library_path) if subdir != "__pycache__"]
for event_handler in event_handler_keys:
    import_event_handler(event_handler)



