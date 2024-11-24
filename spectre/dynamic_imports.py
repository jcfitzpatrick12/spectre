# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from importlib import import_module

def import_target_modules(caller_file: str, # __file__ in the calling context for the library
                          caller_name: str, # __name__ in the calling context for the library
                          target_module: str # the module we are looking to dynamically import
) -> None: 
    # fetch the directory path for the __init__.py in the library directory
    library_dir_path = os.path.dirname(caller_file)
    # list all subdirectories in the library directory
    subdirs = [x.name for x in os.scandir(library_dir_path) if x.is_dir() and (x.name != "__pycache__")]
    # for each subdirectory, try and import the target module
    for subdir in subdirs:
        full_module_name = f"{caller_name}.{subdir}.{target_module}"
        import_module(full_module_name)



