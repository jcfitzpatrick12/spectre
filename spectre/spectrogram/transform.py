# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from datetime import datetime, timedelta

from spectre.utils import array_helpers, datetime_helpers
from spectre.spectrogram.Spectrogram import Spectrogram
from cfg import CONFIG


def frequency_chop(input_S: Spectrogram, 
                   start_freq_MHz: float | int, 
                   end_freq_MHz: float | int) -> Spectrogram:
    
    is_entirely_below_frequency_range = (start_freq_MHz < input_S.freq_MHz[0] and end_freq_MHz < input_S.freq_MHz[0])
    is_entirely_above_frequency_range = (start_freq_MHz > input_S.freq_MHz[-1] and end_freq_MHz > input_S.freq_MHz[-1])
    # if the requested frequency range is out of bounds for the spectrogram return None
    if is_entirely_below_frequency_range or is_entirely_above_frequency_range:
        return None
    
    #find the index of the nearest matching frequency bins in the spectrogram
    start_index = array_helpers.find_closest_index(start_freq_MHz, input_S.freq_MHz)
    end_index = array_helpers.find_closest_index(end_freq_MHz, input_S.freq_MHz)
    
    # enforce distinct start and end indices
    if start_index == end_index:
        raise ValueError(f"Start and end indices are equal! Got start_index: {start_index} and end_index: {end_index}.")  
    
    # if start index is more than end index, swap the ordering so to enforce start_index <= end_index
    if start_index > end_index:
        start_index, end_index = end_index, start_index
    
    # chop the spectrogram accordingly
    transformed_dynamic_spectra = input_S.dynamic_spectra[start_index:end_index+1, :]
    transformed_freq_MHz = input_S.freq_MHz[start_index:end_index+1]

    # if the background spectrum is specified, chop identically in frequency
    if input_S.background_spectrum:
        transformed_background_spectrum = input_S.background_spectrum[start_index:end_index+1]
    
    # return the spectrogram instance
    return Spectrogram(
        transformed_dynamic_spectra,
        input_S.time_seconds,
        transformed_freq_MHz,
        input_S.tag,
        chunk_start_time = input_S.chunk_start_time,
        microsecond_correction = input_S.microsecond_correction,
        spectrum_type = input_S.spectrum_type,
        background_spectrum = transformed_background_spectrum,
        background_interval = input_S.background_interval
        
    )


def time_chop(input_S: Spectrogram, 
              start_time: str, 
              end_time: str, 
              time_format = CONFIG.default_time_format) -> Spectrogram | None:
    

    # spectre does not currently support time chop for non-datetime assigned spectrograms
    if input_S.chunk_start_time is None:
        raise ValueError(f"Input spectrogram is missing chunk start time. Time chop not yet supported for non-datetime assigned spectrograms.")
    
    # parse the strings as datetimes
    start_datetime = datetime.strptime(start_time, time_format)
    end_datetime = datetime.strptime(end_time, time_format)

    # if the requested time range is out of bounds for the spectrogram return None
    is_entirely_below_time_range = (start_datetime < input_S.datetimes[0] and end_datetime < input_S.datetimes[0])
    is_entirely_above_time_range = (start_datetime > input_S.datetimes[-1] and end_datetime > input_S.datetimes[-1])
    if is_entirely_below_time_range or is_entirely_above_time_range:
        return None
    
    start_index = datetime_helpers.find_closest_index(start_datetime, input_S.datetimes)
    end_index = datetime_helpers.find_closest_index(end_datetime, input_S.datetimes)
    
    if start_index == end_index:
        raise ValueError(f"Start and end indices are equal! Got start_index: {start_index} and end_index: {end_index}.")
    
    if start_index > end_index:
        start_index, end_index = end_index, start_index

    # chop the spectrogram 
    transformed_dynamic_spectra = input_S.dynamic_spectra[:, start_index:end_index+1]

    # chop the time seconds array
    transformed_time_seconds = input_S.time_seconds[start_index:end_index+1]
    #translate the chopped time seconds array to start at zero
    transformed_time_seconds -= transformed_time_seconds[0]

    # compute the new start datetime following the time chop
    transformed_start_datetime = input_S.datetimes[start_index]
    # parse the chunk start time (as string)
    transformed_chunk_start_time = datetime.strftime(transformed_start_datetime, CONFIG.default_time_format)
    # and compute the microsecond correction
    transformed_microsecond_correction = transformed_start_datetime.microsecond

    return Spectrogram(transformed_dynamic_spectra, 
                       transformed_time_seconds, 
                       input_S.freq_MHz, 
                       input_S.tag, 
                       chunk_start_time = transformed_chunk_start_time,
                       microsecond_correction = transformed_microsecond_correction,
                       spectrum_type = input_S.spectrum_type,
                       background_spectrum = None, # reset the background spectrum
                       background_interval = None # reset the background interval
                       )


def time_average(input_S: Spectrogram, 
                 average_over: int) -> Spectrogram:
    
    # spectre does not currently support averaging of non-datetime assigned spectrograms
    if input_S.chunk_start_time is None:
        raise ValueError(f"Input spectrogram is missing chunk start time. Averaging is not yet supported for non-datetime assigned spectrograms.")
    
    # if the user has requested no averaging, just return the same instance unchanged
    if average_over == 1:
        return input_S

    # average the dynamic spectra array
    transformed_dynamic_spectra = array_helpers.average_array(input_S.dynamic_spectra, average_over, axis=1)
    # average the time seconds array s.t. the ith averaged spectrum is assigned the 
    transformed_time_seconds = array_helpers.average_array(input_S.time_seconds, average_over)

    # We need to assign timestamps to the averaged spectrums in the spectrograms. The natural way to do this
    # is to assign the i'th averaged spectrogram to the i'th averaged time stamp. From this,
    # we then need to compute the chunk start time to assig to the first averaged spectrum,
    # and update the microsecond correction.
    
    # define the initial spectrum as the spectrum at time index 0 in the spectrogram
    # then, averaged_t0 is the seconds elapsed between the input intial spectrum and the averaged intial spectrum
    averaged_t0 = transformed_time_seconds[0]
    # compute the updated chunk start time and the updated microsecond correction based on averaged_t0
    updated_corrected_start_datetime = input_S.corrected_start_datetime + timedelta(seconds = averaged_t0)
    # then, compute the transformed chunk start time and microsecond correction
    transformed_chunk_start_time = updated_corrected_start_datetime.strftime(CONFIG.default_time_format)
    transformed_microsecond_correction = updated_corrected_start_datetime.microsecond

    # finally, translate the averaged time seconds to begin at t=0 [s]
    transformed_time_seconds -= transformed_time_seconds[0]
    return Spectrogram(transformed_dynamic_spectra, 
                       transformed_time_seconds, 
                       input_S.freq_MHz, 
                       input_S.tag,
                       chunk_start_time = transformed_chunk_start_time,
                       microsecond_correction = transformed_microsecond_correction,
                       spectrum_type = input_S.spectrum_type,
                       background_spectrum = None, # reset the background spectrum
                       background_interval = None, # reset the background interval
                       )


def frequency_average(input_S: Spectrogram, 
                      average_over: int) -> Spectrogram:
    
    # if the user has requested no averaging, just return the same instance unchanged
    if average_over == 1:
        return input_S

    # We need to assign physical frequencies to the averaged spectrums in the spectrograms.
    # is to assign the i'th averaged spectral component to the i'th averaged frequency.
    # average the dynamic spectra array
    transformed_dynamic_spectra = array_helpers.average_array(input_S.dynamic_spectra, average_over, axis=0)
    transformed_freq_MHz = array_helpers.average_array(input_S.freq_MHz, average_over)
    transformed_background_spectrum = array_helpers.average_array(input_S.background_spectrum, average_over)

    return Spectrogram(transformed_dynamic_spectra, 
                       input_S.time_seconds, 
                       transformed_freq_MHz, 
                       input_S.tag,
                       chunk_start_time = input_S.chunk_start_time, 
                       microsecond_correction = input_S.microsecond_correction,
                       spectrum_type = input_S.spectrum_type,
                       background_spectrum = transformed_background_spectrum, 
                       background_interval = input_S.background_spectrum
                       )



# we assume that the spectrogram list is ORDERED chronologically
# we assume there is no time overlap in any of the spectrograms in the list
def join_spectrograms(spectrogram_list: list[Spectrogram]) -> Spectrogram:

    # check that the length of the list is non-zero
    num_spectrograms = len(spectrogram_list)
    if num_spectrograms == 0:
        raise ValueError(f"Input list of spectrograms is empty!")
    
    # extract the first element of the list, and use this as a reference for comparison
    # input validations.
    S_reference = spectrogram_list[0] 

    # perform checks on each spectrogram in teh list
    for S in spectrogram_list:
        if not np.all(np.equal(S.freq_MHz, S_reference.freq_MHz)):
            raise ValueError(f"All spectrograms must have identical frequency ranges.")
        if S.tag != S_reference.tag:
            raise ValueError(f"All tags must be equal for each spectrogram in the input list!")
        if S.spectrum_type != S_reference.spectrum_type:
            raise ValueError(f"All units must be equal for each spectrogram in the input list!")
        if S.chunk_start_time is None:
            raise ValueError(f"All spectrograms must have chunk_start_time set. Received {S.chunk_start_time}.")


    # build a list of the time array of each spectrogram in the list
    conc_datetimes = np.concatenate([S.datetimes for S in spectrogram_list])
    # find the total number of time stamps
    num_total_time_bins = len(conc_datetimes)
    # find the total number of frequency bins (we can safely now use the first)
    num_total_freq_bins = len(S_reference.freq_MHz)
    # create an empty numpy array to hold the joined spectrograms
    transformed_dynamic_spectra = np.empty((num_total_freq_bins, num_total_time_bins))

    start_index = 0
    for S in spectrogram_list:
        end_index = start_index + len(S.time_seconds)
        transformed_dynamic_spectra[:, start_index:end_index] = S.dynamic_spectra
        start_index = end_index

    transformed_time_seconds = datetime_helpers.seconds_elapsed(conc_datetimes)
    # check the transformed time seconds are strictly increasing
    array_helpers.check_strictly_increasing(transformed_time_seconds)

    # compute the microsecond correction
    transformed_microsecond_correction = conc_datetimes[0].microsecond

    return Spectrogram(transformed_dynamic_spectra, 
                       transformed_time_seconds, 
                       S_reference.freq_MHz, 
                       S_reference.tag, 
                       chunk_start_time = S_reference.chunk_start_time,
                       microsecond_correction = transformed_microsecond_correction,
                       spectrum_type = S_reference.spectrum_type,
                       background_spectrum = None, # reset the background spectrum
                       background_interval = None # reset the background interval
                       )


