# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
import datetime
import typing
import math

from ._array_operations import find_closest_index, average_array, time_elapsed
from ._spectrogram import Spectrogram


def frequency_chop(
    spectrogram: Spectrogram, start_frequency: float, end_frequency: float
) -> Spectrogram:
    """
    Extracts a portion of the spectrogram within the specified frequency range.

    :param spectrogram: The input spectrogram to process.
    :param start_frequency: The starting frequency of the desired range (Hz).
    :param end_frequency: The ending frequency of the desired range (Hz).
    :raises ValueError: If the specified frequency range is entirely outside the spectrogram's frequency range.
    :raises ValueError: If the start and end indices for the frequency range are identical.
    :return: A new spectrogram containing only the specified frequency range.
    """
    is_entirely_below_frequency_range = (
        start_frequency < spectrogram.frequencies[0]
        and end_frequency < spectrogram.frequencies[0]
    )
    is_entirely_above_frequency_range = (
        start_frequency > spectrogram.frequencies[-1]
        and end_frequency > spectrogram.frequencies[-1]
    )
    if is_entirely_below_frequency_range or is_entirely_above_frequency_range:
        raise ValueError(
            f"The requested frequency interval is entirely out of range of the input spectrogram."
        )

    # find the index of the nearest matching frequency bins in the spectrogram
    start_index = find_closest_index(
        np.float32(start_frequency), spectrogram.frequencies
    )
    end_index = find_closest_index(np.float32(end_frequency), spectrogram.frequencies)

    # enforce distinct start and end indices
    if start_index == end_index:
        raise ValueError(
            f"Start and end indices are equal! Got start_index: {start_index} and end_index: {end_index}"
        )

    # if start index is more than end index, swap the ordering so to enforce start_index <= end_index
    if start_index > end_index:
        start_index, end_index = end_index, start_index

    # chop the spectrogram accordingly
    transformed_dynamic_spectra = spectrogram.dynamic_spectra[
        start_index : end_index + 1, :
    ]
    transformed_frequencies = spectrogram.frequencies[start_index : end_index + 1]

    return Spectrogram(
        transformed_dynamic_spectra,
        spectrogram.times,
        transformed_frequencies,
        spectrogram.spectrum_unit,
        spectrogram.start_datetime,
    )


def time_chop(
    spectrogram: Spectrogram,
    start_datetime: datetime.datetime,
    end_datetime: datetime.datetime,
) -> Spectrogram:
    """
    Extracts a portion of the spectrogram within the specified time range.

    :param spectrogram: The input spectrogram to process.
    :param start_datetime: The starting time of the desired range.
    :param end_datetime: The ending time of the desired range.
    :raises ValueError: If the specified time range is entirely outside the spectrogram's time range.
    :raises ValueError: If the start and end indices for the time range are identical.
    :return: A new spectrogram containing only the specified time range.
    """
    start_datetime64 = np.datetime64(start_datetime)
    end_datetime64 = np.datetime64(end_datetime)

    is_entirely_below_time_range = (
        start_datetime64 < spectrogram.datetimes[0]
        and end_datetime64 < spectrogram.datetimes[0]
    )
    is_entirely_above_time_range = (
        start_datetime64 > spectrogram.datetimes[-1]
        and end_datetime64 > spectrogram.datetimes[-1]
    )
    if is_entirely_below_time_range or is_entirely_above_time_range:
        raise ValueError(
            f"Requested time interval is entirely out of range of the input spectrogram."
        )

    # find the index of the nearest matching spectrums in the spectrogram.
    start_index = find_closest_index(start_datetime64, spectrogram.datetimes)
    end_index = find_closest_index(end_datetime64, spectrogram.datetimes)

    # enforce distinct start and end indices
    if start_index == end_index:
        raise ValueError(
            f"Start and end indices are equal! Got start_index: {start_index} and end_index: {end_index}"
        )

    # if start index is more than end index, swap the ordering so to enforce start_index <= end_index
    if start_index > end_index:
        start_index, end_index = end_index, start_index

    # chop the spectrogram accordingly
    transformed_dynamic_spectra = spectrogram.dynamic_spectra[
        :, start_index : end_index + 1
    ]
    transformed_start_datetime = spectrogram.datetimes[start_index]

    # chop the times array and translate such that the first spectrum to t=0 [s]
    transformed_times = spectrogram.times[start_index : end_index + 1]
    transformed_times -= transformed_times[0]

    return Spectrogram(
        transformed_dynamic_spectra,
        transformed_times,
        spectrogram.frequencies,
        spectrogram.spectrum_unit,
        transformed_start_datetime,
    )


def _validate_and_compute_average_over(
    original_resolution: float, resolution: typing.Optional[float], average_over: int
) -> int:
    """
    Validates the input parameters and computes `average_over` if `resolution` is specified.

    :param resolution: The desired resolution for averaging. Mutually exclusive with `average_over`.
    :param average_over: The number of consecutive spectrums to average over. Mutually exclusive with `resolution`.
    :param original_resolution: The original resolution (e.g., time or frequency).
    :raises ValueError: If neither or both `resolution` and `average_over` are specified.
    :return: The computed or validated `average_over` value.
    """
    if (resolution is None) and (average_over == 1):
        return average_over

    if not (resolution is not None) ^ (average_over != 1):
        raise ValueError(
            "Exactly one of 'resolution' or 'average_over' must be specified."
        )

    if resolution is not None:
        return max(1, math.floor(resolution / original_resolution))

    else:
        return average_over


def time_average(
    spectrogram: Spectrogram,
    resolution: typing.Optional[float] = None,
    average_over: int = 1,
) -> Spectrogram:
    """
    Performs time averaging on the spectrogram data.

    :param spectrogram: The input spectrogram to process.
    :param resolution: The desired time resolution for averaging (seconds). Mutually exclusive with `average_over`.
    :param average_over: The number of consecutive time points to average. Mutually exclusive with `resolution`.
    :raises NotImplementedError: If the spectrogram lacks a defined start datetime.
    :raises ValueError: If neither or both `resolution` and `average_over` are specified.
    :return: A new spectrogram with time-averaged data.
    """
    if not spectrogram.start_datetime_is_set:
        raise NotImplementedError(
            "Time averaging is not supported for spectrograms without an assigned start datetime."
        )

    average_over = _validate_and_compute_average_over(
        spectrogram.time_resolution, resolution, average_over
    )

    transformed_dynamic_spectra = average_array(
        spectrogram.dynamic_spectra, average_over, axis=1
    )

    # Take the start time of each block (this preserves the original start time.)
    transformed_times = spectrogram.times[0::average_over]

    return Spectrogram(
        transformed_dynamic_spectra,
        transformed_times,
        spectrogram.frequencies,
        spectrogram.spectrum_unit,
        spectrogram.start_datetime,
    )


def frequency_average(
    spectrogram: Spectrogram,
    resolution: typing.Optional[float] = None,
    average_over: int = 1,
) -> Spectrogram:
    """
    Performs frequency averaging on the spectrogram data.

    :param spectrogram: The input spectrogram to process.
    :param resolution: The desired frequency resolution for averaging (Hz). Mutually exclusive with `average_over`.
    :param average_over: The number of consecutive frequency bins to average. Mutually exclusive with `resolution`.
    :raises ValueError: If neither or both `resolution` and `average_over` are specified.
    :return: A new spectrogram with frequency-averaged data.
    """
    average_over = _validate_and_compute_average_over(
        spectrogram.frequency_resolution, resolution, average_over
    )

    # Perform averaging
    transformed_dynamic_spectra = average_array(
        spectrogram.dynamic_spectra, average_over, axis=0
    )
    transformed_frequencies = average_array(spectrogram.frequencies, average_over)

    return Spectrogram(
        transformed_dynamic_spectra,
        spectrogram.times,
        transformed_frequencies,
        spectrogram.spectrum_unit,
        spectrogram.start_datetime,
    )


def join_spectrograms(spectrograms: list[Spectrogram]) -> Spectrogram:
    """
    Joins multiple spectrograms into a single spectrogram along the time axis.

    :param spectrograms: A list of spectrograms to combine.
    :raises ValueError: If the input list is empty.
    :raises ValueError: If spectrograms have mismatched frequency ranges.
    :raises ValueError: If spectrograms have different tags.
    :raises ValueError: If spectrograms have differing spectrum units.
    :raises ValueError: If any spectrogram lacks a defined start datetime.
    :return: A new spectrogram combining all input spectrograms along the time axis.
    """
    # check that the length of the list is non-zero
    num_spectrograms = len(spectrograms)
    if num_spectrograms == 0:
        raise ValueError(f"Input list of spectrograms is empty!")

    # extract the first element of the list, and use this as a reference for comparison
    # input validations.
    reference_spectrogram = spectrograms[0]

    # perform checks on each spectrogram in teh list
    for spectrogram in spectrograms:
        if not np.all(
            np.equal(spectrogram.frequencies, reference_spectrogram.frequencies)
        ):
            raise ValueError(f"All spectrograms must have identical frequency ranges")
        if spectrogram.spectrum_unit != reference_spectrogram.spectrum_unit:
            raise ValueError(
                f"All units must be equal for each spectrogram in the input list!"
            )
        if not spectrogram.start_datetime_is_set:
            raise ValueError(f"All spectrograms must have their start datetime set.")

    # Concatenate all dynamic spectra directly along the time axis
    transformed_dynamic_spectra = np.hstack(
        [spectrogram.dynamic_spectra for spectrogram in spectrograms]
    )

    transformed_times = time_elapsed(
        np.concatenate([s.datetimes for s in spectrograms])
    )

    return Spectrogram(
        transformed_dynamic_spectra,
        transformed_times,
        reference_spectrogram.frequencies,
        reference_spectrogram.spectrum_unit,
        reference_spectrogram.start_datetime,
    )
