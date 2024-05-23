import numpy as np
import warnings

def find_closest_index(val, ar: np.ndarray, enforce_strict_bounds = False) -> int:
    # Ensure input array is not empty
    if ar.size == 0:
        raise ValueError("Input array 'ar' is empty.")

    try:
        # Attempt to convert inputs to numpy array of type float
        ar = np.asarray(ar, dtype=float)
        val = float(val)
    except ValueError:
        # Handle case where conversion to float is not possible
        raise ValueError("Both 'val' and elements of 'ar' must be valid numeric types.")
    
    if val > np.nanmax(ar):
        error_message = f"Value {val} is strictly larger than the maximum of the array {np.nanmax(ar)}. Returning index of maximum value."
        if enforce_strict_bounds:
            raise ValueError(error_message)
        else:
            pass
            # warnings.warn(error_message)
    if val < np.nanmin(ar):
        error_message = f"Value {val} is strictly less than the minimum of the array {np.nanmin(ar)}. Returning index of minimum value."
        if enforce_strict_bounds:
            raise ValueError(error_message)
        else:
            pass
            # warnings.warn(error_message)
    
    # Compute absolute differences and find the index of the minimum
    closest_index = np.argmin(np.abs(ar - val))
    return closest_index


def compute_resolution(array: np.ndarray) -> float:
    # Check that the array is one-dimensional
    if array.ndim != 1:
        raise ValueError("Input array must be one-dimensional.")
    
    if len(array) < 2:
        raise ValueError("Input array must contain at least two elements.")
    
    # Calculate differences between consecutive elements.
    resolutions = np.diff(array)
    
    # if the resolution is not constant across the array, 
    if not np.allclose(resolutions, resolutions[0]):
        warnings.warn("Resolution is not consistent across all elements.", UserWarning)

    return np.nanmedian(resolutions)


def average_array(array: np.ndarray, average_over: int, axis=0) -> np.ndarray:
    # each "full block" will contain (along the requested axis) average_over elements
    
    max_axis_index = len(np.shape(array)) - 1
    if axis > max_axis_index: # zero indexing on specifying axis, so minus one
        raise ValueError(f"Requested axis is out of range of array dimensions. Axis: {axis}, max axis index: {max_axis_index}")

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
        array = np.pad(array, padding_shape, mode='constant', constant_values=np.nan)
    
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


def move_to_front(lst: list, target) -> list:
    if not all(isinstance(item, type(lst[0])) for item in lst):
        raise ValueError("All elements in the list must be of the same type.")

    if target not in lst:
        raise ValueError("The target is not in the list.")

    non_target_items = [item for item in lst if item != target]
    target_count = lst.count(target)
    return [target] * target_count + non_target_items


def normalise_integral_to_unity(yvals: np.ndarray, xvals: np.ndarray):
    return yvals/np.trapz(yvals, xvals)


def normalise_peak_intensity(yvals: np.ndarray):
    return yvals/np.nanmax(yvals)


def background_subtract(yvals: np.ndarray, background_indices: list | None):
    if background_indices is None:
        warnings.warn(f"No background interval set. Subtracting total mean.")
        yvals -= np.nanmean(yvals)
    else:
        yvals -= np.nanmean(yvals[background_indices[0]:
                                  background_indices[1]])
    return yvals