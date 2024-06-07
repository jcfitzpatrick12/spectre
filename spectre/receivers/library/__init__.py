# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import importlib
import pkgutil 

# the contents of this __init__ will dynamically import all mounts, and add each of those
# which is decorated to the global list of mounts
# Iterate through all receiver directories within the library
library_path = os.path.dirname(__file__)
expected_modules_for_receiver = ['CaptureMount', 'CaptureConfigMount']

def import_from_receiver(receiver):
    # create the full path to the receiver, 
    receiver_path = os.path.join(library_path, receiver)
    # ensure this path describes a directory, not a file
    if not os.path.isdir(receiver_path):
        return

    # list all subdirectories
    dir_contents = [d for d in os.listdir(receiver_path) if not d == "__pycache__"]

    if "gr" not in dir_contents:
        raise NotADirectoryError(f"Could not find \"gr\" directory for receiver {receiver}.")

    gr_path = os.path.join(receiver_path, 'gr')

    if not os.path.isdir(gr_path):
        raise NotADirectoryError(f"{gr_path} is not a directory. \"gr\" must be a specified as a directory.")
    

    if "mounts" not in dir_contents:
        raise NotADirectoryError(f"Could not find \"mounts\" directory for receiver {receiver}.")
    
    
    mounts_path = os.path.join(receiver_path, 'mounts')

    if not os.path.isdir(mounts_path):
        raise NotADirectoryError(f"{mounts_path} is not a directory. \"mounts\" must be a specified as a directory.")
    
    # Import all modules in the receiver's 'mounts' subdirectory
    for _, module_name, _ in pkgutil.iter_modules([mounts_path]):
        if module_name in expected_modules_for_receiver:
            # found_modules.add()
            full_module_name = f'spectre.receivers.library.{receiver}.mounts.{module_name}'
            importlib.import_module(full_module_name)


# list all directories which are not __pycache__
receivers = [subdir for subdir in os.listdir(library_path) if subdir != "__pycache__"]
for receiver in receivers:
    import_from_receiver(receiver)



