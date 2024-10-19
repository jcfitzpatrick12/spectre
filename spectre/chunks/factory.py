# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# after we decorate all chunks, we can import the chunk_key -> chunk maps
from spectre.chunks.chunk_register import chunk_map
from spectre.chunks.base import BaseChunk
from spectre.file_handlers.json import CaptureConfigHandler
from spectre.exceptions import ChunkNotFoundError


def get_chunk(chunk_key: str) -> BaseChunk:
    try:
        Chunk = chunk_map[chunk_key]
        return Chunk
    except KeyError:
        valid_chunk_keys = list(chunk_map.keys())
        raise ChunkNotFoundError(f"No chunk found for the chunk key: {chunk_key}. Valid chunk keys are: {valid_chunk_keys}")


def get_chunk_from_tag(tag: str) -> BaseChunk:
    # if we are dealing with a callisto chunk, the chunk key is equal to the tag
    if "callisto" in tag:
        chunk_key = "callisto"
    # otherwise, we fetch the chunk key from the capture config
    else:
        capture_config_handler = CaptureConfigHandler(tag)
        capture_config = capture_config_handler.read()
        chunk_key = capture_config.get('chunk_key')
    return get_chunk(chunk_key)
