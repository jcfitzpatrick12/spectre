# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

#  Global dictionaries to hold the mappings
chunk_map = {}

# classes decorated with @register_chunk([CHUNK_KEY])
# will be added to chunk_map
def register_chunk(chunk_key: str):
    _LOGGER.info(f"Registering chunk with key {chunk_key}")
    def decorator(cls):
        chunk_map[chunk_key] = cls
        return cls
    return decorator

