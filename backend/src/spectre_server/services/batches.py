# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import Optional
from os.path import splitext
from os import walk

from spectre_core.logs import log_call
from spectre_core.batches import Batches, BatchKey, get_batch_cls_from_tag
from spectre_core.config import get_batches_dir_path, trim_spectre_data_dir_path
from spectre_core.capture_configs import CaptureConfig
from spectre_core.spectrograms import validate_analytically

@log_call
def get_tags(
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> list[str]:
    """Look for tags with existing batch files in the file system.

    :param year: Filter batch files by the numeric year, defaults to None
    :param month: Filter batch files by the numeric month, defaults to None
    :param day: Filter batch files by the numeric day, defaults to None
    :return: A list of unique tags which have existing batch files in the file system.
    """
    batches_dir_path = get_batches_dir_path(year, month, day)
    batch_files = [f for (_, _, files) in walk(batches_dir_path) for f in files]
    tags = set()
    for batch_file in batch_files:
        batch_base_name, _ = splitext(batch_file)
        tag = batch_base_name.split("_")[1]
        tags.add(tag)

    return sorted(list(tags))


@log_call
def get_batch_keys(
) -> list[str]:
    """Get a list of all defined batch keys."""
    return [batch_key.value for batch_key in BatchKey]


@log_call
def get_batch_files_for_tag(
    tag: str,
    extensions: Optional[list[str]] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None
) -> list[str]:
    """Look for all batch files in the file system with a given tag.
    
    :param tag: Search for batch files with this tag.
    :param extensions: Filter batch files with this extension, defaults to None
    :param year: Filter batch files by the numeric year, defaults to None
    :param month: Filter batch files by the numeric month, defaults to None
    :param day: Filter batch files by the numeric day, defaults to None
    :return: The file paths of all batch files under the input tag which exist in the file system,
    relative to the mounted volume
    """
    if extensions is None:
        extensions = []
    
    batch_cls = get_batch_cls_from_tag(tag)
    batches = Batches(tag,
                      batch_cls,
                      year=year,
                      month=month,
                      day=day)
    
    batch_files = []
    for batch in batches:
        # if no extensions are specified, look for ALL defined extensions for that batch
        if not extensions:
            extensions = batch.extensions

        for extension in extensions:
            if batch.has_file(extension):
                batch_file = batch.get_file(extension)
                batch_files.append( trim_spectre_data_dir_path(batch_file.file_path) )
    return batch_files


@log_call
def delete_batch_files(
    tag: str,
    extensions: list[str],
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> list[str]:
    """Delete batch files.

    :param tag: Delete batch files with this tag.
    :param extensions: Delete only batch files with specific extensions. If an empty list is 
    passed, batch files with any valid extension will be deleted.
    :param year: Delete only batch files from this numeric year. Defaults to None. If no year, month, 
    or day is specified, files from any year will be deleted.
    :param month: Delete only batch files from this numeric month. Defaults to None. If a year is 
    specified but not a month, all files from that year will be deleted.
    :param day: Delete only batch files from this numeric day. Defaults to None. If both year and month 
    are specified but not a day, all files from that year and month will be deleted.
    :return: The file paths of batch files which have been successfully deleted,
    relative to the mounted volume.
    
    """
    batch_cls = get_batch_cls_from_tag(tag)
    batches = Batches(tag, 
                      batch_cls,
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
                deleted_file_names.append( trim_spectre_data_dir_path(batch_file.file_path) )

    return deleted_file_names


@log_call
def get_analytical_test_results(
    tag: str,
    absolute_tolerance: float
) -> dict[str, dict[str, bool | dict[float, bool]]]:
    """Compare all spectrograms with the input tag to analytically derived solutions.
    
    The tag must be associated with a `Test` receiver capture config.

    :param tag: The tag of the batches containing the spectrogram data.
    :param absolute_tolerance: Tolerance level for numerical comparisons.
    :return: The test results per spectrogram file, as a serialisable dictionary.
    """
    capture_config = CaptureConfig(tag)
    
    batch_cls = get_batch_cls_from_tag(tag)
    batches = Batches(tag, batch_cls)
    
    results_per_batch = {}
    for batch in batches:
        if batch.spectrogram_file.exists:
            spectrogram = batch.read_spectrogram()
            test_results = validate_analytically(spectrogram, 
                                                 capture_config,
                                                 absolute_tolerance)
            rel_path = trim_spectre_data_dir_path(batch.spectrogram_file.file_name)
            results_per_batch[rel_path] = test_results.to_dict()

    return results_per_batch