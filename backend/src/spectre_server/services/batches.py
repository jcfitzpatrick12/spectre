# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import Optional, cast
from os.path import splitext
from os import walk
from datetime import date, time, datetime

from spectre_core.logs import log_call
from spectre_core.batches import (
    Batches, BatchKey, get_batch_cls_from_tag
)
from spectre_core.config import (
    get_batches_dir_path, TimeFormat
)
from spectre_core.capture_configs import CaptureConfig
from spectre_core.spectrograms import (
    validate_analytically, frequency_chop, Spectrogram, TimeType
)
from spectre_core.plotting import (
    PanelStack, SpectrogramPanel
)


def _make_batches(
    tag: str,
    obs_date: date,
):
    return Batches(tag, 
                   get_batch_cls_from_tag(tag),
                   obs_date.year,
                   obs_date.month,
                   obs_date.day)


def _get_spectrogram(
    batches: Batches,
    obs_date: date,
    start_time: time,
    end_time: time,
    lower_freq: Optional[float],
    upper_freq: Optional[float]
) -> Spectrogram:
    start_datetime = datetime.combine(obs_date, start_time)
    end_datetime   = datetime.combine(obs_date, end_time)
    s = batches.get_spectrogram(start_datetime, end_datetime)
    
    if lower_freq is not None and upper_freq is not None:
        return frequency_chop(s, lower_freq, upper_freq)
    elif lower_freq is not None and upper_freq is None:
        return frequency_chop(s, lower_freq, s.frequencies[-1])
    elif lower_freq is None and upper_freq is not None:
        return frequency_chop(s, s.frequencies[0], upper_freq)
    else:
        return s

 
@log_call
def create_plot(
    tags: list[str],
    figsize: tuple[int, int],
    obs_date: str,
    start_time: str,
    end_time: str,
    lower_freq: Optional[float] = None,
    upper_freq: Optional[float] = None,
    log_norm: bool = False,
    dBb: bool = False,
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
) -> str:
    """
    Create a plot visualising spectrogram data over a specified time interval and optional frequency range.

    :param tags: A list of spectrogram tags to plot. The first tag is used to save the resulting batch file.
    :param figsize: The `matplotlib` figure size as a tuple of (width, height).
    :param obs_date: The observation start date, in the format `%Y-%m-%d`.
    :param start_time: The observation start time (UTC), in the format `%H:%M:%S`.
    :param end_time: The observation end time (UTC), in the format `%H:%M:%S`.
    :param lower_freq: The lower bound of the frequency range in Hz. If not specified, the minimum available 
    frequency is used for each spectrogram. Defaults to None.
    :param upper_freq: The upper bound of the frequency range in Hz. If not specified, the maximum available 
    frequency is used for each spectrogram. Defaults to None.
    :param log_norm: If True, normalises the spectrograms to the 0-1 range on a logarithmic scale. Defaults to False.
    :param dBb: If True, plots the spectrograms in decibels above the background. Defaults to False.
    :param vmin: The minimum value for the colourmap. Applies only if `dBb` is True.
    :param vmax: The maximum value for the colourmap. Applies only if `dBb` is True.
    :return: The file path of the newly created batch file containing the plot.
    """
    # Parse the datetimes
    obs_date_as_date   = datetime.strptime(obs_date, TimeFormat.DATE).date()
    start_time_as_time = datetime.strptime(start_time, TimeFormat.TIME).time()
    end_time_as_time   = datetime.strptime(end_time, TimeFormat.TIME).time()
    
    # Filter the batch files for each tag.
    batches = {tag: _make_batches(tag, obs_date_as_date) for tag in tags}
    
    # Create the spectrograms.
    spectrograms = []
    for tag in tags:
        spectrograms.append( 
            _get_spectrogram(batches[tag], 
                             obs_date_as_date, 
                             start_time_as_time, 
                             end_time_as_time,
                             lower_freq,
                             upper_freq) 
        )
    
    
    # Create the plot, and save it as a batch file.
    # TODO: Permit relative time type too.
    panel_stack = PanelStack(time_type=TimeType.DATETIMES, 
                             non_interactive=True,
                             figsize=figsize)
    for spectrogram in spectrograms:
        panel_stack.add_panel( SpectrogramPanel(spectrogram,
                                                log_norm=log_norm,
                                                dBb=dBb,
                                                vmin=vmin,
                                                vmax=vmax) )   
    return panel_stack.save()


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
    as absolute paths within the container's file system.
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
                batch_files.append(batch_file.file_path)
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
    as absolute paths within the container's file system.
    
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
                deleted_file_names.append(batch_file.file_path)

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
            abs_path = batch.spectrogram_file.file_path
            results_per_batch[abs_path] = test_results.to_dict()

    return results_per_batch