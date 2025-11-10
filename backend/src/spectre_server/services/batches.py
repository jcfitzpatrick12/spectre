# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing
import datetime
import os

import spectre_core.batches
import spectre_core.receivers
import spectre_core.config
import spectre_core.spectrograms
import spectre_core.plotting


def _get_batch(
    file_name: str,
    year: int,
    month: int,
    day: int,
) -> spectre_core.batches.Base:
    start_time, tag, _ = spectre_core.batches.parse_batch_file_name(file_name)
    batches = spectre_core.batches.Batches(
        spectre_core.receivers.get_batch_cls(tag),
        tag,
        spectre_core.config.paths.get_batches_dir_path(year, month, day),
    )
    return batches[start_time]


def _get_batch_file(
    file_name: str,
) -> spectre_core.batches.BatchFile:
    start_time, _, extension = spectre_core.batches.parse_batch_file_name(file_name)
    dt = datetime.datetime.strptime(start_time, spectre_core.config.TimeFormat.DATETIME)
    batch = _get_batch(file_name, dt.year, dt.month, dt.day)
    return batch.get_file(extension)


@spectre_core.logs.log_call
def get_batch_file(
    file_name: str,
) -> str:
    """Get the file path of a batch file which exists in the file system.

    :param file_name: Look for any batch file with this file name.
    :return: The file path of the batch file if it exists in the file system, as an absolute path within the container's file system.
    """

    batch_file = _get_batch_file(file_name)
    return batch_file.file_path


@spectre_core.logs.log_call
def get_batch_files(
    tags: list[str],
    extensions: list[str],
    year: typing.Optional[int] = None,
    month: typing.Optional[int] = None,
    day: typing.Optional[int] = None,
) -> list[str]:
    """Get the file paths of batch files which exist in the file system.

    :param tags: Look for batch files with these tags. If no tags are specified, look for batch files with any tag.
    :param extensions: Look for batch files with these extensions. If no extensions are specified, look for batch files with any extension.
    :param year: Only look for batch files under this year, defaults to None. If year, month and day are unspecified, look for batch files under any year.
    :param month: Only look for batch files under this month, defaults to None. If year is specified, but not month and day, look for batch files under that year.
    :param day: Only look for batch files under this day, defaults to None. If year and month are specified, but not day, look for batch files under that month and year.
    :return: The file paths of all batch files under the input tag which exist in the file system, as absolute paths within the container's file system.
    """
    if not tags:
        tags = get_tags(year, month, day)

    batch_files = []
    for tag in tags:
        batches = spectre_core.batches.Batches(
            spectre_core.receivers.get_batch_cls(tag),
            tag,
            spectre_core.config.paths.get_batches_dir_path(year, month, day),
        )

        for batch in batches:
            # If no extensions are specified, look for batch files with any (defined) extension.
            # Relabel to something that's not `extensions` to stop shadowing
            exts = extensions or batch.extensions

            for extension in exts:
                # Just ignore undefined extensions.
                if extension not in batch.extensions:
                    continue

                if batch.has_file(extension):
                    batch_file = batch.get_file(extension)
                    batch_files.append(batch_file.file_path)
    return sorted(batch_files)


@spectre_core.logs.log_call
def delete_batch_file(
    file_name: str,
    dry_run: bool = False,
) -> str:
    """Remove a batch file from the file system.

    :param file_name: Delete the batch file with this file name.
    :param dry_run: If True, display which files would be deleted without actually deleting them. Defaults to False
    :return: The file path of the deleted batch file, as an absolute file path in the container's file system.
    """
    batch_file = _get_batch_file(file_name)
    if not dry_run:
        batch_file.delete()
    return batch_file.file_path


@spectre_core.logs.log_call
def delete_batch_files(
    tags: list[str],
    extensions: list[str],
    year: typing.Optional[int] = None,
    month: typing.Optional[int] = None,
    day: typing.Optional[int] = None,
    dry_run: bool = False,
) -> list[str]:
    """Bulk remove batch files from the file system.

    Use with caution, the current implementation contains little safeguarding.

    :param tags: Only batch files with these tags will be deleted. If no tags are provided, no batch files will be deleted.
    :param extensions: Only batch files with these extensions will be deleted. If no extensions are provided, no batch files will be deleted.
    :param year: Only delete batch files under this year. Defaults to None. If no year, month, or day is specified, files from any year will be deleted.
    :param month: Only delete batch files under this month. Defaults to None. If a year is specified, but not a month, all files from that year will be deleted.
    :param day: Only delete batch files under this day. Defaults to None. If both year and month are specified, but not the day, all files from that year and month will be deleted.
    :param dry_run: If True, display which files would be deleted without actually deleting them. Defaults to False
    :return: The file paths of batch files which have been successfully deleted, as absolute paths within the container's file system.
    """
    deleted_batch_files = []
    for tag in tags:
        batch_cls = spectre_core.receivers.get_batch_cls(tag)
        batches = spectre_core.batches.Batches(
            batch_cls,
            tag,
            spectre_core.config.paths.get_batches_dir_path(year, month, day),
        )

        for batch in batches:
            for extension in extensions:

                # Just ignore undefined extensions.
                if extension not in batch.extensions:
                    continue

                if batch.has_file(extension):
                    batch_file = batch.get_file(extension)
                    if not dry_run:
                        batch_file.delete()
                    deleted_batch_files.append(batch_file.file_path)
    return deleted_batch_files


def _get_signal_generator(mode: str) -> spectre_core.receivers.SignalGenerator:
    return typing.cast(
        spectre_core.receivers.SignalGenerator,
        spectre_core.receivers.get_receiver(
            spectre_core.receivers.ReceiverName.SIGNAL_GENERATOR, mode
        ),
    )


@spectre_core.logs.log_call
def get_analytical_test_results(
    file_name: str, absolute_tolerance: float
) -> dict[str, bool | dict[float, bool]]:
    """Validate spectrograms produced by the signal generator against analytically derived solutions.

    The batch file must be the spectrogram file for the batch.

    :param file_name: The batch file name.
    :param absolute_tolerance: The absolute tolerance to which we consider agreement with the
    analytical solution for each spectral component. See the 'atol' keyword argument for `np.isclose`.
    :return: The test results for the spectrogram file, as a serialisable dictionary.
    """
    batch_file = _get_batch_file(file_name)

    _, tag, _ = spectre_core.batches.parse_batch_file_name(file_name)

    spectrogram = batch_file.read()

    if not isinstance(spectrogram, spectre_core.spectrograms.Spectrogram):
        raise ValueError(
            f"The file '{batch_file.file_name}' does not contain a spectrogram."
        )

    config = spectre_core.receivers.read_config(tag)
    if not config.receiver_name == spectre_core.receivers.ReceiverName.SIGNAL_GENERATOR:
        raise ValueError(
            f"Expected receiver name '{spectre_core.receivers.ReceiverName.SIGNAL_GENERATOR}', but got '{config.receiver_name}."
        )
    signal_generator = _get_signal_generator(config.receiver_mode)
    return signal_generator.validate_analytically(
        spectrogram,
        signal_generator.model_validate(config.parameters),
        absolute_tolerance,
    )


@spectre_core.logs.log_call
def get_tags(
    year: typing.Optional[int] = None,
    month: typing.Optional[int] = None,
    day: typing.Optional[int] = None,
) -> list[str]:
    """Look for tags with existing batch files in the file system.

    :param year: Only look for batch files under this year. Defaults to None. If none of year, month and day are specified, find tags under any year.
    :param month: Only look for batch files under this month. Defaults to None. If year is specified, but not month or day, find tags under that year.
    :param day: Only look for batch files under this day. Defaults to None. If year and month are specified, but not day, find tags under that month.
    :return: A list of unique tags which have existing batch files in the file system.
    """
    batches_dir_path = spectre_core.config.paths.get_batches_dir_path(year, month, day)
    batch_file_names = [
        os.path.basename(f)
        for (_, _, files) in os.walk(batches_dir_path)
        for f in files
    ]
    tags = set()
    for batch_file_name in batch_file_names:
        _, tag, _ = spectre_core.batches.parse_batch_file_name(batch_file_name)
        tags.add(tag)
    return sorted(list(tags))


def _make_batches(
    tag: str,
    obs_date: datetime.date,
):
    return spectre_core.batches.Batches(
        spectre_core.receivers.get_batch_cls(tag),
        tag,
        spectre_core.config.paths.get_batches_dir_path(
            obs_date.year, obs_date.month, obs_date.day
        ),
    )


def _get_spectrogram(
    batches: spectre_core.batches.Batches,
    obs_date: datetime.date,
    start_time: datetime.time,
    end_time: datetime.time,
    lower_freq: typing.Optional[float],
    upper_freq: typing.Optional[float],
) -> spectre_core.spectrograms.Spectrogram:
    start_datetime = datetime.datetime.combine(obs_date, start_time)
    end_datetime = datetime.datetime.combine(obs_date, end_time)
    s = batches.get_spectrogram(start_datetime, end_datetime)

    if lower_freq is not None and upper_freq is not None:
        return spectre_core.spectrograms.frequency_chop(s, lower_freq, upper_freq)
    elif lower_freq is not None and upper_freq is None:
        return spectre_core.spectrograms.frequency_chop(
            s, lower_freq, s.frequencies[-1]
        )
    elif lower_freq is None and upper_freq is not None:
        return spectre_core.spectrograms.frequency_chop(s, s.frequencies[0], upper_freq)
    else:
        return s


@spectre_core.logs.log_call
def create_plot(
    tags: list[str],
    figsize: tuple[int, int],
    obs_date: str,
    start_time: str,
    end_time: str,
    lower_freq: typing.Optional[float] = None,
    upper_freq: typing.Optional[float] = None,
    log_norm: bool = False,
    dBb: bool = False,
    vmin: typing.Optional[float] = None,
    vmax: typing.Optional[float] = None,
) -> str:
    """
    Create a stacked plot of spectrogram data over a specified time interval, then save it to the
    file system as a batch file.

    :param tags: The batch file tag. Specifying multiple tags yields a stacked plot over the same time frame. The first
    tag indicates which batch the plot will be saved under.
    :param figsize: The `matplotlib` figure size as a tuple of (width, height).
    :param obs_date: The observation start date, in the format `%Y-%m-%d`.
    :param start_time: The observation start time (UTC), in the format `%H:%M:%S`.
    :param end_time: The observation end time (UTC), in the format `%H:%M:%S`.
    :param lower_freq: The lower bound of the frequency range in Hz. If not specified, the minimum available
    frequency is used for each spectrogram. Defaults to None.
    :param upper_freq: The upper bound of the frequency range in Hz. If not specified, the maximum available
    frequency is used for each spectrogram. Defaults to None.
    :param log_norm: If True, normalises the spectrograms to the 0-1 range on a logarithmic scale. Defaults to False.
    :param dBb: If True, use units of decibels above the background. Defaults to False.
    :param vmin: The minimum value for the colourmap. Applies only if `dBb` is True.
    :param vmax: The maximum value for the colourmap. Applies only if `dBb` is True.
    :return: The file path of the newly created batch file containing the plot, as an absolute path in the container's file system.
    """
    # Parse the datetimes
    obs_date_as_date = datetime.datetime.strptime(
        obs_date, spectre_core.config.TimeFormat.DATE
    ).date()
    start_time_as_time = datetime.datetime.strptime(
        start_time, spectre_core.config.TimeFormat.TIME
    ).time()
    end_time_as_time = datetime.datetime.strptime(
        end_time, spectre_core.config.TimeFormat.TIME
    ).time()

    # Filter the batch files for each tag.
    batches = {tag: _make_batches(tag, obs_date_as_date) for tag in tags}

    # Create the spectrograms.
    spectrograms = []
    for tag in tags:
        spectrograms.append(
            _get_spectrogram(
                batches[tag],
                obs_date_as_date,
                start_time_as_time,
                end_time_as_time,
                lower_freq,
                upper_freq,
            )
        )

    # Create the plot, and save it as a batch file.
    # TODO: Permit relative time type too.
    panel_stack = spectre_core.plotting.PanelStack(
        time_type=spectre_core.spectrograms.TimeType.DATETIMES,
        non_interactive=True,
        figsize=figsize,
    )
    for spectrogram in spectrograms:
        panel_stack.add_panel(
            spectre_core.plotting.SpectrogramPanel(
                spectrogram, log_norm=log_norm, dBb=dBb, vmin=vmin, vmax=vmax
            )
        )
    return panel_stack.save(tag)
