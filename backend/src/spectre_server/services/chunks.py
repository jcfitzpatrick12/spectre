# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import Optional
from os.path import splitext
from os import walk

from spectre_core.logging import log_call
from spectre_core.chunks import Chunks
from spectre_core.cfg import get_chunks_dir_path


@log_call
def get_chunk_files(tag: str,
                    extensions: Optional[list[str]] = None,
                    year: Optional[int] = None,
                    month: Optional[int] = None,
                    day: Optional[int] = None,
) -> list[str]:
    """Get the file names of all existing chunk files.
    
    Optional filtering by date and by extension.
    """
    if extensions is None:
        extensions = []
    chunks = Chunks(tag, 
                    year=year, 
                    month=month,
                    day=day)
    chunk_files = []
    for chunk in chunks:
        # if no extensions are specified, look for ALL defined extensions for that chunk
        if not extensions:
            extensions = chunk.extensions

        for extension in extensions:
            if chunk.has_file(extension):
                chunk_file = chunk.get_file(extension)
                chunk_files.append(chunk_file.file_name)
    return chunk_files


@log_call
def delete_chunk_files(tag: str,
                       extensions: list[str],
                       year: Optional[int] = None,
                       month: Optional[int] = None,
                       day: Optional[int] = None,
) -> None:
    """Delete chunk files.
    
    Files to be deleted are specified according to date, and extension.
    """
    chunks = Chunks(tag, 
                    year=year, 
                    month=month,
                    day=day)
    
    deleted_file_names = []
    for chunk in chunks:
        for extension in extensions:
            if chunk.has_file(extension):
                chunk_file = chunk.get_file(extension)
                chunk_file.delete()
                _LOGGER.info(f"File deleted: {chunk_file.file_name}")
                deleted_file_names.append(chunk_file.file_name)

    return deleted_file_names


@log_call
def get_tags(year: Optional[int] = None,
             month: Optional[int] = None,
             day: Optional[int] = None,
) -> list[str]:
    """Get a list of all unique tags, with corresponding chunk files"""
    chunks_dir_path = get_chunks_dir_path(year, month, day)
    chunk_files = [f for (_, _, files) in walk(chunks_dir_path) for f in files]
    tags = set()
    for chunk_file in chunk_files:
        chunk_base_name, _ = splitext(chunk_file)
        tag = chunk_base_name.split("_")[1]
        tags.add(tag)

    return sorted(list(tags))