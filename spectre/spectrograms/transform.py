# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from datetime import datetime, timedelta

from spectre.spectrograms.array_operations import (
    find_closest_index
)
from spectre.spectrograms.spectrogram import Spectrogram
from spectre.cfg import (
    DEFAULT_DATETIME_FORMAT
)


def _average_array(array: np.ndarray, average_over: int, axis=0) -> np.ndarray:

    # Check if average_over is an integer
    if type(average_over) != int:
        raise TypeError(f"average_over must be an integer. Got {type(average_over)}")

    # Get the size of the specified axis which we will average over
    axis_size = array.shape[axis]
    # Check if average_over is within the valid range
    if not 1 <= average_over <= axis_size:
        raise ValueError(f"average_over must be between 1 and the length of the axis ({axis_size})")
    
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


def frequency_chop(input_spectrogram: Spectrogram, 
                   start_frequency: float | int, 
                   end_frequency: float | int) -> Spectrogram:
    
    is_entirely_below_frequency_range = (start_frequency < input_spectrogram.frequencies[0] and end_frequency < input_spectrogram.frequencies[0])
    is_entirely_above_frequency_range = (start_frequency > input_spectrogram.frequencies[-1] and end_frequency > input_spectrogram.frequencies[-1])
    # if the requested frequency range is out of bounds for the spectrogram return None
    if is_entirely_below_frequency_range or is_entirely_above_frequency_range:
        return None
    
    #find the index of the nearest matching frequency bins in the spectrogram
    start_index = find_closest_index(start_frequency, input_spectrogram.frequencies)
    end_index = find_closest_index(end_frequency, input_spectrogram.frequencies)
    
    # enforce distinct start and end indices
    if start_index == end_index:
        raise ValueError(f"Start and end indices are equal! Got start_index: {start_index} and end_index: {end_index}")  
    
    # if start index is more than end index, swap the ordering so to enforce start_index <= end_index
    if start_index > end_index:
        start_index, end_index = end_index, start_index
    
    # chop the spectrogram accordingly
    transformed_dynamic_spectra = input_spectrogram.dynamic_spectra[start_index:end_index+1, :]
    transformed_frequencies = input_spectrogram.frequencies[start_index:end_index+1]

    # if the background spectrum is specified, chop identically in frequency
    if not (input_spectrogram.background_spectrum is None):
        transformed_background_spectrum = input_spectrogram.background_spectrum[start_index:end_index+1]
    
    # return the spectrogram instance
    return Spectrogram(transformed_dynamic_spectra,
                       input_spectrogram.times,
                       transformed_frequencies,
                       input_spectrogram.tag,
                       chunk_start_time = input_spectrogram.chunk_start_time,
                       microsecond_correction = input_spectrogram.microsecond_correction,
                       spectrum_type = input_spectrogram.spectrum_type,
                       background_spectrum = transformed_background_spectrum,
                       background_interval = input_spectrogram.background_interval
                       )


def time_chop(input_spectrogram: Spectrogram, 
              start_time: str, 
              end_time: str, 
              time_format: str = DEFAULT_DATETIME_FORMAT) -> Spectrogram | None:
    

    # spectre does not currently support time chop for non-datetime assigned spectrograms
    if input_spectrogram.chunk_start_time is None:
        raise ValueError(f"Input spectrogram is missing chunk start time. Time chop not yet supported for non-datetime assigned spectrograms")
    
    # parse the strings as datetimes
    start_datetime = datetime.strptime(start_time, time_format)
    end_datetime = datetime.strptime(end_time, time_format)

    # if the requested time range is out of bounds for the spectrogram return None
    is_entirely_below_time_range = (start_datetime < input_spectrogram.datetimes[0] and end_datetime < input_spectrogram.datetimes[0])
    is_entirely_above_time_range = (start_datetime > input_spectrogram.datetimes[-1] and end_datetime > input_spectrogram.datetimes[-1])
    if is_entirely_below_time_range or is_entirely_above_time_range:
        return None
    
    start_index = find_closest_index(start_datetime, input_spectrogram.datetimes)
    end_index = find_closest_index(end_datetime, input_spectrogram.datetimes)
    
    if start_index == end_index:
        raise ValueError(f"Start and end indices are equal! Got start_index: {start_index} and end_index: {end_index}")
    
    if start_index > end_index:
        start_index, end_index = end_index, start_index

    # chop the spectrogram 
    transformed_dynamic_spectra = input_spectrogram.dynamic_spectra[:, start_index:end_index+1]

    # chop the times array
    transformed_times = input_spectrogram.times[start_index:end_index+1]
    #translate the chopped times array to start at zero
    transformed_times -= transformed_times[0]

    # compute the new start datetime following the time chop
    transformed_start_datetime = input_spectrogram.datetimes[start_index]
    # parse the chunk start time (as string)
    transformed_chunk_start_time = datetime.strftime(transformed_start_datetime, DEFAULT_DATETIME_FORMAT)
    # and compute the microsecond correction
    transformed_microsecond_correction = transformed_start_datetime.microsecond

    return Spectrogram(transformed_dynamic_spectra, 
                       transformed_times, 
                       input_spectrogram.frequencies, 
                       input_spectrogram.tag, 
                       chunk_start_time = transformed_chunk_start_time,
                       microsecond_correction = transformed_microsecond_correction,
                       spectrum_type = input_spectrogram.spectrum_type,
                       background_spectrum = None, # reset the background spectrum
                       background_interval = None # reset the background interval
                       )


def time_average(input_spectrogram: Spectrogram, 
                 average_over: int) -> Spectrogram:
    
    # spectre does not currently support averaging of non-datetime assigned spectrograms
    if input_spectrogram.chunk_start_time is None:
        raise ValueError(f"Input spectrogram is missing chunk start time. Averaging is not yet supported for non-datetime assigned spectrograms")
    
    # if the user has requested no averaging, just return the same instance unchanged
    if average_over == 1:
        return input_spectrogram

    # average the dynamic spectra array
    transformed_dynamic_spectra = _average_array(input_spectrogram.dynamic_spectra, average_over, axis=1)
    # average the times array s.t. the ith averaged spectrum is assigned the 
    transformed_times = _average_array(input_spectrogram.times, average_over)

    # We need to assign timestamps to the averaged spectrums in the spectrograms. The natural way to do this
    # is to assign the i'th averaged spectrogram to the i'th averaged time stamp. From this,
    # we then need to compute the chunk start time to assig to the first averaged spectrum,
    # and update the microsecond correction.
    
    # define the initial spectrum as the spectrum at time index 0 in the spectrogram
    # then, averaged_t0 is the seconds elapsed between the input intial spectrum and the averaged intial spectrum
    averaged_t0 = float(transformed_times[0])
    # compute the updated chunk start time and the updated microsecond correction based on averaged_t0
    updated_corrected_start_datetime = input_spectrogram.corrected_start_datetime + timedelta(seconds = averaged_t0)
    # then, compute the transformed chunk start time and microsecond correction
    transformed_chunk_start_time = updated_corrected_start_datetime.strftime(DEFAULT_DATETIME_FORMAT)
    transformed_microsecond_correction = updated_corrected_start_datetime.microsecond

    # finally, translate the averaged time seconds to begin at t=0 [s]
    transformed_times -= transformed_times[0]
    return Spectrogram(transformed_dynamic_spectra, 
                       transformed_times, 
                       input_spectrogram.frequencies, 
                       input_spectrogram.tag,
                       chunk_start_time = transformed_chunk_start_time,
                       microsecond_correction = transformed_microsecond_correction,
                       spectrum_type = input_spectrogram.spectrum_type,
                       background_spectrum = None, # reset the background spectrum
                       background_interval = None, # reset the background interval
                       )


def frequency_average(input_spectrogram: Spectrogram, 
                      average_over: int) -> Spectrogram:
    
    # if the user has requested no averaging, just return the same instance unchanged
    if average_over == 1:
        return input_spectrogram

    # We need to assign physical frequencies to the averaged spectrums in the spectrograms.
    # is to assign the i'th averaged spectral component to the i'th averaged frequency.
    # average the dynamic spectra array
    transformed_dynamic_spectra = _average_array(input_spectrogram.dynamic_spectra, average_over, axis=0)
    transformed_frequencies = _average_array(input_spectrogram.frequencies, average_over)
    transformed_background_spectrum = _average_array(input_spectrogram.background_spectrum, average_over)

    return Spectrogram(transformed_dynamic_spectra, 
                       input_spectrogram.times, 
                       transformed_frequencies, 
                       input_spectrogram.tag,
                       chunk_start_time = input_spectrogram.chunk_start_time, 
                       microsecond_correction = input_spectrogram.microsecond_correction,
                       spectrum_type = input_spectrogram.spectrum_type,
                       background_spectrum = transformed_background_spectrum, 
                       background_interval = input_spectrogram.background_interval
                       )


def _time_elapsed(datetimes: np.ndarray) -> np.ndarray:
    # Extract the first datetime to use as the reference point
    base_time = datetimes[0]
    # Calculate elapsed time in seconds for each datetime in the list
    elapsed_time = [(dt - base_time).total_seconds() for dt in datetimes]
    # Convert the list of seconds to a NumPy array of type float32
    return np.array(elapsed_time, dtype=np.float32)

# we assume that the spectrogram list is ORDERED chronologically
# we assume there is no time overlap in any of the spectrograms in the list
def join_spectrograms(spectrograms: list[Spectrogram]) -> Spectrogram:

    # check that the length of the list is non-zero
    num_spectrograms = len(spectrograms)
    if num_spectrograms == 0:
        raise ValueError(f"Input list of spectrograms is empty!")
    
    # extract the first element of the list, and use this as a reference for comparison
    # input validations.
    reference_spectrogram = spectrograms[0] 

    # perform checks on each spectrogram in teh list
    for spectrogram in spectrograms:
        if not np.all(np.equal(spectrogram.frequencies, reference_spectrogram.frequencies)):
            raise ValueError(f"All spectrograms must have identical frequency ranges")
        if spectrogram.tag != reference_spectrogram.tag:
            raise ValueError(f"All tags must be equal for each spectrogram in the input list!")
        if spectrogram.spectrum_type != reference_spectrogram.spectrum_type:
            raise ValueError(f"All units must be equal for each spectrogram in the input list!")
        if spectrogram.chunk_start_time is None:
            raise ValueError(f"All spectrograms must have chunk_start_time set. Received {spectrogram.chunk_start_time}")


    # build a list of the time array of each spectrogram in the list
    conc_datetimes = np.concatenate([s.datetimes for s in spectrograms])
    # find the total number of time stamps
    num_total_time_bins = len(conc_datetimes)
    # find the total number of frequency bins (we can safely now use the first)
    num_total_freq_bins = len(reference_spectrogram.frequencies)
    # create an empty numpy array to hold the joined spectrograms
    transformed_dynamic_spectra = np.empty((num_total_freq_bins, num_total_time_bins))

    start_index = 0
    for spectrogram in spectrograms:
        end_index = start_index + len(spectrogram.times)
        transformed_dynamic_spectra[:, start_index:end_index] = spectrogram.dynamic_spectra
        start_index = end_index

    transformed_times = _time_elapsed(conc_datetimes)
    
    transformed_microsecond_correction = conc_datetimes[0].microsecond

    return Spectrogram(transformed_dynamic_spectra, 
                       transformed_times, 
                       reference_spectrogram.frequencies, 
                       reference_spectrogram.tag, 
                       chunk_start_time = reference_spectrogram.chunk_start_time,
                       microsecond_correction = transformed_microsecond_correction,
                       spectrum_type = reference_spectrogram.spectrum_type,
                       background_spectrum = None, # reset the background spectrum
                       background_interval = None # reset the background interval
                       )


