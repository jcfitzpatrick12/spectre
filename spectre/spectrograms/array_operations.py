# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from datetime import datetime
from typing import Union, Sequence

def find_closest_index(
    target_value: float | datetime, 
    array: np.ndarray, 
    enforce_strict_bounds: bool = False
) -> int:
    # Ensure input array is a numpy array
    array = np.asarray(array)

    # Convert to datetime64 if necessary
    if isinstance(target_value, datetime) or np.issubdtype(array.dtype, np.datetime64):
        target_value = np.datetime64(target_value)
        array = array.astype('datetime64[ns]')
    else:
        target_value = float(target_value)
        array = array.astype(float)

    # Check bounds if strict enforcement is required
    if enforce_strict_bounds:
        max_value, min_value = np.nanmax(array), np.nanmin(array)
        if target_value > max_value:
            raise ValueError(f"Target value {target_value} exceeds max array value {max_value}.")
        if target_value < min_value:
            raise ValueError(f"Target value {target_value} is less than min array value {min_value}.")

    # Find the index of the closest value
    return np.argmin(np.abs(array - target_value))


def normalise_peak_intensity(yvals: np.ndarray) -> np.ndarray:
    return yvals/np.nanmax(yvals)


def compute_resolution(array: np.ndarray) -> float:
    # Check that the array is one-dimensional
    if array.ndim != 1:
        raise ValueError("Input array must be one-dimensional.")
    
    if len(array) < 2:
        raise ValueError("Input array must contain at least two elements.")
    
    # Calculate differences between consecutive elements.
    resolutions = np.diff(array)

    return np.nanmedian(resolutions)


def subtract_background(yvals: np.ndarray, background_indices: list | None) -> np.ndarray:
    if background_indices is None:
        yvals -= np.nanmean(yvals)
    else:
        yvals -= np.nanmean(yvals[background_indices[0]:
                                  background_indices[1]])
    return yvals