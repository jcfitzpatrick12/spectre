# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import importlib
import pkgutil 

library_path = os.path.dirname(__file__)

def import_chunk(chunk_key: str):
    # create the full path to the chunk
    chunk_path = os.path.join(library_path, chunk_key)
    # ensure this path describes a directory, not a file
    if not os.path.isdir(chunk_path):
        return

    # list all subdirectories
    dir_contents = [d for d in os.listdir(chunk_path) if not d == "__pycache__"]

    if "chunk.py" not in dir_contents:
        raise FileNotFoundError(f"Chunk directories must contain the file chunk.py - not found in {chunk_path}")
    
    full_module_name = f'spectre.file_handlers.chunks.library.{chunk_key}.chunk'
    # import the Chunk module for that particular Chunk type
    importlib.import_module(full_module_name)


# list all directories which are not __pycache__
chunk_keys = [subdir for subdir in os.listdir(library_path) if subdir != "__pycache__"]
for chunk_key in chunk_keys:
    import_chunk(chunk_key)



