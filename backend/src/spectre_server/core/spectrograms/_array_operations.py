# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing

import numpy as np
import numpy.typing as npt


def average_array(
    array: npt.NDArray[np.float32], average_over: int, axis: int = 0
) -> npt.NDArray[np.float32]:
    """
    Averages elements of an array in blocks along a specified axis.

    :param array: Input array to be averaged.
    :param average_over: Number of elements in each averaging block.
    :param axis: Axis along which to perform the averaging, defaults to 0.
    :raises TypeError: If `average_over` is not an integer.
    :raises ValueError: If `average_over` is not in the range [1, size of the axis].
    :raises ValueError: If `axis` is out of bounds for the array.
    :return: Array of averaged values along the specified axis.
    """

    # Get the size of the specified axis which we will average over
    axis_size = array.shape[axis]
    # Check if average_over is within the valid range
    if not 1 <= average_over <= axis_size:
        raise ValueError(
            f"average_over must be between 1 and the length of the axis ({axis_size})"
        )

    max_axis_index = len(np.shape(array)) - 1
    if axis > max_axis_index:  # zero indexing on specifying axis, so minus one
        raise ValueError(
            f"Requested axis is out of range of array dimensions. Axis: {axis}, max axis index: {max_axis_index}"
        )

    # find the number of elements in the requested axis
    num_elements = array.shape[axis]

    # find the number of "full blocks" to average over
    num_full_blocks = num_elements // average_over
    # if num_elements is not exactly divisible by average_over, we will have some elements left over
    # these remaining elements will be padded with nans to become another full block
    remainder = num_elements % average_over

    # if there exists a remainder, pad the last block
    if remainder != 0:
        # initialise an array to hold the padding shape
        padding_shape = [(0, 0)] * array.ndim
        # pad after the last column in the requested axis
        padding_shape[axis] = (0, average_over - remainder)
        # pad with nan values (so to not contribute towards the mean computation)
        array = np.pad(array, padding_shape, mode="constant", constant_values=np.nan)

    # initalise a list to hold the new shape
    new_shape = list(array.shape)
    # update the shape on the requested access (to the number of blocks we will average over)
    new_shape[axis] = num_full_blocks + (1 if remainder else 0)
    # insert a new dimension, with the size of each block
    new_shape.insert(axis + 1, average_over)
    # and reshape the array to sort the array into the relevant blocks.
    reshaped_array = array.reshape(new_shape)
    # average over the newly created axis, essentially averaging over the blocks.
    averaged_array = np.nanmean(reshaped_array, axis=axis + 1)
    # return the averaged array
    return averaged_array


T = typing.TypeVar("T", np.float32, np.datetime64)


def find_closest_index(
    target_value: T, array: npt.NDArray[T], enforce_strict_bounds: bool = False
) -> int:
    """
    Finds the index of the closest value to a target in a given array, with optional bounds enforcement.

    :param target_value: The value to find the closest match for.
    :param array: The array to search within.
    :param enforce_strict_bounds: If True, raises an error if the target value is outside the array bounds. Defaults to False.
    :return: The index of the closest value in the array.
    :raises ValueError: If `enforce_strict_bounds` is True and `target_value` is outside the array bounds.
    """
    # Check bounds if strict enforcement is required
    if enforce_strict_bounds:
        max_value, min_value = np.nanmax(array), np.nanmin(array)
        if target_value > max_value:
            raise ValueError(
                f"Target value {target_value} exceeds max array value {max_value}"
            )
        if target_value < min_value:
            raise ValueError(
                f"Target value {target_value} is less than min array value {min_value}"
            )

    # Find the index of the closest value
    return int(np.argmin(np.abs(array - target_value)))


def normalise_peak_intensity(array: npt.NDArray[np.float32]) -> npt.NDArray[np.float32]:
    """
    Normalises an array by its peak intensity.

    :param array: Input array to normalise.
    :return: Array normalised such that its maximum value is 1. NaN values are ignored.
    """
    return array / np.nanmax(array)


def compute_resolution(array: npt.NDArray[np.float32]) -> float:
    """
    Computes the median resolution of a one-dimensional array.

    :param array: Input one-dimensional array of values.
    :return: The median of differences between consecutive elements in the array.
    :raises ValueError: If the input array is not one-dimensional or contains fewer than two elements.
    """
    # Check that the array is one-dimensional
    if array.ndim != 1:
        raise ValueError("Input array must be one-dimensional")

    if len(array) < 2:
        raise ValueError("Input array must contain at least two elements")

    # Calculate differences between consecutive elements.
    resolutions = np.diff(array)
    return float(np.nanmedian(resolutions))


def compute_range(array: npt.NDArray[np.float32]) -> float:
    """
    Computes the range of a one-dimensional array as the difference between its last and first elements.

    :param array: Input one-dimensional array of values.
    :return: The range of the array (last element minus first element).
    :raises ValueError: If the input array is not one-dimensional or contains fewer than two elements.
    """
    # Check that the array is one-dimensional
    if array.ndim != 1:
        raise ValueError("Input array must be one-dimensional")

    if len(array) < 2:
        raise ValueError("Input array must contain at least two elements")
    return float(array[-1] - array[0])


def subtract_background(
    array: npt.NDArray[np.float32], start_index: int, end_index: int
) -> npt.NDArray[np.float32]:
    """
    Subtracts the mean of a specified background range from all elements in an array.

    :param array: Input array from which the background mean will be subtracted.
    :param start_index: Start index of the background range (inclusive).
    :param end_index: End index of the background range (inclusive).
    :return: Array with the background mean subtracted.
    """
    array -= np.nanmean(array[start_index : end_index + 1])
    return array


def time_elapsed(datetimes: npt.NDArray[np.datetime64]) -> npt.NDArray[np.float32]:
    """Convert an array of datetimes to seconds elapsed."""
    return (datetimes - datetimes[0]).astype("timedelta64[us]") / np.timedelta64(1, "s")
