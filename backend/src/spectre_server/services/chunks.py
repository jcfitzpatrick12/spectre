# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import Optional, Any
from os.path import splitext
from os import walk

from spectre_core.logging import log_call
from spectre_core.chunks import Chunks
from spectre_core.config import get_chunks_dir_path
from spectre_core.capture_configs import CaptureConfig
from spectre_core.spectrograms import validate_analytically


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


@log_call
def get_chunk_files_for_tag(tag: Optional[str],
                            extensions: Optional[list[str]] = None,
                            year: Optional[int] = None,
                            month: Optional[int] = None,
                            day: Optional[int] = None
) -> list[str]:
    """Get a list of files under a specified tag."""
    if extensions is None:
        extensions = []
    
    chunks = Chunks(tag,
                    year,
                    month,
                    day)
    
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
def get_chunk_files(tags: Optional[list[str]],
                    extensions: Optional[list[str]] = None,
                    year: Optional[int] = None,
                    month: Optional[int] = None,
                    day: Optional[int] = None,
) -> list[str]:
    """Get the file names of all existing chunk files.
    
    Optional filtering by tag, date and by extension.
    """
    tags = tags or get_tags(year, month, day)
    chunk_files = []
    for tag in tags:
        chunk_files += get_chunk_files_for_tag(tag,
                                               extensions,
                                               year,
                                               month,
                                               day)
    return sorted(chunk_files)


@log_call
def delete_chunk_files(tag: str,
                       extensions: list[str],
                       year: Optional[int] = None,
                       month: Optional[int] = None,
                       day: Optional[int] = None,
) -> list[str]:
    """Delete chunk files.
    
    Files to be deleted are specified according to date, and extension.
    """
    chunks = Chunks(tag, 
                    year=year, 
                    month=month,
                    day=day)
    
    deleted_file_names = []
    for chunk in chunks:
        if not extensions:
            extensions = chunk.extensions
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



@log_call
def get_analytical_test_results(
    tag: str,
    absolute_tolerance: float
) -> dict[str, bool | dict[float, bool]]:
    capture_config = CaptureConfig(tag)
    
    results_per_chunk = {}
    chunks = Chunks(tag)
    for chunk in chunks:
        if chunk.has_file("fits"):
            chunk_file = chunk.get_file("fits")
            spectrogram = chunk_file.read()
            test_results = validate_analytically(spectrogram, 
                                                 capture_config,
                                                 absolute_tolerance)
            results_per_chunk[chunk_file.file_name] = test_results.to_dict()

    return results_per_chunk