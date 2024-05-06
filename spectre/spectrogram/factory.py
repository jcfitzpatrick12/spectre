import numpy as np
from datetime import datetime

from spectre.utils import array_helpers, datetime_helpers
from spectre.spectrogram.Spectrogram import Spectrogram
from cfg import CONFIG


def frequency_chop(S: Spectrogram, start_freq_MHz: any, end_freq_MHz: any) -> Spectrogram:
    #find the index of the nearest matching frequencies in the input spectrogram
    start_index = array_helpers.find_closest_index(start_freq_MHz,S.freq_MHz)
    end_index = array_helpers.find_closest_index(end_freq_MHz,S.freq_MHz)

    if start_index>end_index:
        start_index, end_index = end_index, start_index

    # #return the default null spectrogram
    if start_index==end_index:
        raise ValueError(f"Start and end indices are equal! Got start_index: {start_index} and end_index: {end_index}.")
    
    # chop the spectrogram accordingly
    chopped_dynamic_spectra = S.dynamic_spectra[start_index:end_index+1, :]
    chopped_freq_MHz = S.freq_MHz[start_index:end_index+1]

    # if necessary, update bvect 
    if S.bvect is None:
        bvect = None
    else:
        bvect = S.bvect[start_index:end_index+1]
    
    return Spectrogram(chopped_dynamic_spectra, 
                       S.time_seconds, 
                       chopped_freq_MHz, 
                       S.tag, 
                       chunk_start_time = S.chunk_start_time, 
                       bvect = bvect, 
                       units = S.units)


def time_chop(S, start_time_as_str: str, end_time_as_str: str, **kwargs) -> Spectrogram:
    time_format = kwargs.get("time_format", CONFIG.default_time_format)

    start_dt = datetime.strptime(start_time_as_str, time_format)
    end_dt = datetime.strptime(end_time_as_str, time_format)

    if (start_dt >= S.datetimes[-1] and end_dt >= S.datetimes[-1]) or (start_dt<= S.datetimes[0] and end_dt <= S.datetimes[0]):
        return None
    
    start_index = datetime_helpers.find_closest_index(start_dt, S.datetimes)
    end_index = datetime_helpers.find_closest_index(end_dt, S.datetimes)

    if start_index>end_index:
        start_index, end_index = end_index, start_index

    if start_index==end_index:
        raise ValueError(f"Start and end indices are equal! Got start_index: {start_index} and end_index: {end_index}.")

    # chop the spectrogram accordingly
    chopped_dynamic_spectra = S.dynamic_spectra[:, start_index:end_index+1]
    chopped_time_seconds = S.time_seconds[start_index:end_index+1]
    #translate the chopped time array to again start at zero
    chopped_time_seconds-=chopped_time_seconds[0]
    # #extract the new chunk_start_time
    chopped_chunk_start_time = datetime.strftime(S.datetimes[start_index], CONFIG.default_time_format)

    return Spectrogram(chopped_dynamic_spectra, 
                       chopped_time_seconds, 
                       S.freq_MHz, 
                       S.tag, 
                       chunk_start_time = S.chunk_start_time,
                       bvect = S.bvect, 
                       units = S.units)


def time_average(S: Spectrogram, average_over: int) -> Spectrogram:
    if average_over == 1:
        return S

    num_temporal_samples = S.dynamic_spectra.shape[1]
    num_full_blocks = num_temporal_samples // average_over
    remainder = num_temporal_samples % average_over

    averaged_dynamic_spectra = array_helpers.average_array(S.dynamic_spectra, average_over, axis=1)
    # Ensuring the time array matches the length of the averaged dynamic_spectra
    block_count = num_full_blocks + (1 if remainder else 0)
    decimated_time_seconds = S.time_seconds[:(block_count * average_over):average_over]

    return Spectrogram(averaged_dynamic_spectra, 
                       decimated_time_seconds, 
                       S.freq_MHz, 
                       S.tag, 
                       chunk_start_time = S.chunk_start_time,
                       bvect=S.bvect, 
                       units = S.units)


def frequency_average(S: Spectrogram, average_over: int) -> Spectrogram:
    if average_over == 1:
        return S

    num_freq_samples = S.dynamic_spectra.shape[0]
    num_full_blocks = num_freq_samples // average_over
    remainder = num_freq_samples % average_over

    averaged_dynamic_spectra = array_helpers.average_array(S.dynamic_spectra, average_over, axis=0)
    averaged_bvect = array_helpers.average_array(S.bvect, average_over, axis=0) if S.bvect is not None else None
    # Ensuring the frequency array matches the length of the averaged dynamic_spectra
    block_count = num_full_blocks + (1 if remainder else 0)
    decimated_freq_MHz = S.freq_MHz[:(block_count * average_over):average_over]

    return Spectrogram(averaged_dynamic_spectra, 
                       S.time_seconds, 
                       decimated_freq_MHz, 
                       S.tag,
                       chunk_start_time = S.chunk_start_time, 
                       bvect=averaged_bvect, 
                       units = S.units)



# assumes that the spectrogram list is ORDERED chronologically.
# assumes there is no time overlap in any of the spectrograms in the list.
def join_spectrograms(spectrogram_list: list) -> Spectrogram:

    # check that the input spectrogram_list is a list
    if not isinstance(spectrogram_list, list):
        raise ValueError(f"Expected a list of spectrograms as input, received {type(spectrogram_list)}")

    # check that the length of the list is non-zero
    num_spectrograms = len(spectrogram_list)
    if num_spectrograms == 0:
        raise ValueError(f"Input list of spectrograms is empty!")
    
    # extract the first element of the list
    Sref = spectrogram_list[0] 

    # ensure all the frequencies of each spectrogram are identical
    for S in spectrogram_list:
        if not np.all(np.equal(S.freq_MHz, Sref.freq_MHz)):
            raise ValueError(f"All spectrograms must have identical frequency ranges.")
        if S.tag != Sref.tag:
            raise ValueError(f"All tags must be equal for each spectrogram in the input list!")
        if S.units != Sref.units:
            raise ValueError(f"All units must be equal for each spectrogram in the input list!")
        if S.chunk_start_time is None:
            raise ValueError(f"All spectrograms must have chunk_start_time set. Received {S.chunk_start_time}.")


    # build a list of the time array of each spectrogram in the list
    conc_datetimes = np.concatenate([S.datetimes for S in spectrogram_list])
    total_time_bins = len(conc_datetimes)
    # find the total number of frequency bins (we can safely now use the first)
    total_freq_bins = len(Sref.freq_MHz)
    conc_dynamic_spectra = np.empty((total_freq_bins, total_time_bins))

    start_index = 0
    for S in spectrogram_list:
        end_index = start_index + len(S.time_seconds)
        conc_dynamic_spectra[:, start_index:end_index] = S.dynamic_spectra
        start_index = end_index

    conc_time_seconds = datetime_helpers.seconds_elapsed(conc_datetimes)

    return Spectrogram(conc_dynamic_spectra, 
                       conc_time_seconds, 
                       Sref.freq_MHz, 
                       Sref.tag, 
                       chunk_start_time = Sref.chunk_start_time,
                       bvect = Sref.bvect, 
                       units = Sref.units)


