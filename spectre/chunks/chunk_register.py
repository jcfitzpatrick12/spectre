# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

#  Global dictionaries to hold the mappings
chunk_map = {}

# classes decorated with @register_chunk([CHUNK_KEY])
# will be added to chunk_map
def register_chunk(chunk_key: str):
    def decorator(cls):
        chunk_map[chunk_key] = cls
        return cls
    return decorator

