# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import importlib
import pkgutil

library_path = os.path.dirname(__file__)

def import_from_receiver(receiver):
    receiver_path = os.path.join(library_path, receiver)
    if not os.path.isdir(receiver_path):
        return

    dir_contents = [d for d in os.listdir(receiver_path) if d != "__pycache__"]

    if "gr" not in dir_contents:
        raise NotADirectoryError(f"Could not find \"gr\" directory for receiver {receiver}.")

    gr_path = os.path.join(receiver_path, 'gr')

    if not os.path.isdir(gr_path):
        raise NotADirectoryError(f"{gr_path} is not a directory. \"gr\" must be specified as a directory.")

    if "receiver.py" not in dir_contents:
        raise ValueError(f"Could not find Receiver.py in {receiver}")

    full_module_name = f'spectre.receivers.library.{receiver}.receiver'
    importlib.import_module(full_module_name)

# List all directories which are not __pycache__
receivers = [subdir for subdir in os.listdir(library_path) if subdir != "__pycache__" and os.path.isdir(os.path.join(library_path, subdir))]
for receiver in receivers:
    import_from_receiver(receiver)
