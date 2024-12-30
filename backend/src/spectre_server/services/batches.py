# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import Optional, Any
from os.path import splitext
from os import walk

from spectre_core.logging import log_call
from spectre_core.batches import Batches
from spectre_core.config import get_batches_dir_path
from spectre_core.capture_configs import CaptureConfig
from spectre_core.spectrograms import validate_analytically


@log_call
def get_tags(year: Optional[int] = None,
             month: Optional[int] = None,
             day: Optional[int] = None,
) -> list[str]:
    """Get a list of all unique tags, with corresponding batch files"""
    batches_dir_path = get_batches_dir_path(year, month, day)
    batch_files = [f for (_, _, files) in walk(batches_dir_path) for f in files]
    tags = set()
    for batch_file in batch_files:
        batch_base_name, _ = splitext(batch_file)
        tag = batch_base_name.split("_")[1]
        tags.add(tag)

    return sorted(list(tags))


@log_call
def get_batch_files_for_tag(tag: Optional[str],
                            extensions: Optional[list[str]] = None,
                            year: Optional[int] = None,
                            month: Optional[int] = None,
                            day: Optional[int] = None
) -> list[str]:
    """Get a list of files under a specified tag."""
    if extensions is None:
        extensions = []
    
    batches = Batches(tag,
                    year,
                    month,
                    day)
    
    batch_files = []
    for batch in batches:
        # if no extensions are specified, look for ALL defined extensions for that batch
        if not extensions:
            extensions = batch.extensions

        for extension in extensions:
            if batch.has_file(extension):
                batch_file = batch.get_file(extension)
                batch_files.append(batch_file.file_name)
    return batch_files


@log_call
def get_batch_files(tags: Optional[list[str]],
                    extensions: Optional[list[str]] = None,
                    year: Optional[int] = None,
                    month: Optional[int] = None,
                    day: Optional[int] = None,
) -> list[str]:
    """Get the file names of all existing batch files.
    
    Optional filtering by tag, date and by extension.
    """
    tags = tags or get_tags(year, month, day)
    batch_files = []
    for tag in tags:
        batch_files += get_batch_files_for_tag(tag,
                                               extensions,
                                               year,
                                               month,
                                               day)
    return sorted(batch_files)


@log_call
def delete_batch_files(tag: str,
                       extensions: list[str],
                       year: Optional[int] = None,
                       month: Optional[int] = None,
                       day: Optional[int] = None,
) -> list[str]:
    """Delete batch files.
    
    Files to be deleted are specified according to date, and extension.
    """
    batches = Batches(tag, 
                    year=year, 
                    month=month,
                    day=day)
    
    deleted_file_names = []
    for batch in batches:
        if not extensions:
            extensions = batch.extensions
        for extension in extensions:
            if batch.has_file(extension):
                batch_file = batch.get_file(extension)
                batch_file.delete()
                _LOGGER.info(f"File deleted: {batch_file.file_name}")
                deleted_file_names.append(batch_file.file_name)

    return deleted_file_names


@log_call
def get_tags(year: Optional[int] = None,
             month: Optional[int] = None,
             day: Optional[int] = None,
) -> list[str]:
    """Get a list of all unique tags, with corresponding batch files"""
    batches_dir_path = get_batches_dir_path(year, month, day)
    batch_files = [f for (_, _, files) in walk(batches_dir_path) for f in files]
    tags = set()
    for batch_file in batch_files:
        batch_base_name, _ = splitext(batch_file)
        tag = batch_base_name.split("_")[1]
        tags.add(tag)

    return sorted(list(tags))



@log_call
def get_analytical_test_results(
    tag: str,
    absolute_tolerance: float
) -> dict[str, bool | dict[float, bool]]:
    capture_config = CaptureConfig(tag)
    
    results_per_batch = {}
    batches = Batches(tag)
    for batch in batches:
        if batch.has_file("fits"):
            batch_file = batch.get_file("fits")
            spectrogram = batch_file.read()
            test_results = validate_analytically(spectrogram, 
                                                 capture_config,
                                                 absolute_tolerance)
            results_per_batch[batch_file.file_name] = test_results.to_dict()

    return results_per_batch