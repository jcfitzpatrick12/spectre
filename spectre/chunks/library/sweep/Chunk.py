# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from typing import Tuple
from scipy.signal import ShortTimeFFT, get_window
from math import floor
from datetime import datetime, timedelta

from cfg import CONFIG
from spectre.chunks.SPECTREChunk import SPECTREChunk
from spectre.chunks.chunk_register import register_chunk
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.chunks.library.sweep.HdrChunk import HdrChunk
from spectre.chunks.library.default.BinChunk import BinChunk
from spectre.chunks.library.default.FitsChunk import FitsChunk

@register_chunk('sweep')
class Chunk(SPECTREChunk):
    def __init__(self, chunk_start_time, tag):
        # Initialize the Chunk with the start time and tag.
        super().__init__(chunk_start_time, tag)
        self.bin = BinChunk(chunk_start_time, tag)
        self.fits = FitsChunk(chunk_start_time, tag)
        self.hdr = HdrChunk(chunk_start_time, tag)
        
        # Initialize some attributes which will be shared amongst private methods when build spectrogram is called
        self.window = None
        self.SFT = None
        self.num_steps_per_sweep = None
        self.num_full_sweeps = None
        self.num_frequencies_per_step = None
        self.num_max_slices_in_step = None

    def build_spectrogram(self,
                          previous_chunk: SPECTREChunk = None) -> Spectrogram:
        # Build and return the spectrogram for the chunk
        sweep_IQ_data = self.bin.read()
        millisecond_correction, sweep_metadata = self.hdr.read()
        # if no previous chunk is specified, the chunk start time for the spectrogram will be set by the current chunk
        chunk_start_time = self.chunk_start_time

        # if the previous chunk is specified, it is indicated we need to reconstruct the initial sweep
        if previous_chunk:
            # the initial sweep will be reconstructed based on the *final* sweep of the previous chunk
            # we define num_full_sweeps in such a way that we can guarantee the final sweep has not yet been processed.
            # so the procedure is well-defined.
            sweep_IQ_data_to_prepend, sweep_metadata_to_prepend = self.__get_final_sweep_previous_chunk(previous_chunk)

            # prepend the new samples and metadata to the start of the existing arrays
            sweep_IQ_data = self.__prepend_sweep_IQ_data(sweep_IQ_data, sweep_IQ_data_to_prepend)
            sweep_metadata = self.__prepend_sweep_metadata(sweep_metadata,
                                                                           sweep_metadata_to_prepend)
            # since the previous chunk has been specified, we need to compute the updated chunk start time and microsecond correction for the spectrogram
            # this can be inferred from the current chunk start time and millisecond correction, along with the number of samples we are prepending
            chunk_start_time, millisecond_correction = self.__get_corrected_timing(millisecond_correction, sweep_metadata_to_prepend)
            pass

        center_frequencies, num_samples = sweep_metadata

        ## add a reconstruction step based on the previous chunk
        microsecond_correction = millisecond_correction * 1000

        time_seconds, freq_MHz, dynamic_spectra = self.__do_STFFT(sweep_IQ_data, 
                                                                  center_frequencies, 
                                                                  num_samples)

        time_seconds = np.array(time_seconds, dtype='float64')
        freq_MHz = np.array(freq_MHz, dtype='float64')
        dynamic_spectra = np.array(dynamic_spectra, dtype='float64')

        return Spectrogram(dynamic_spectra, 
                           time_seconds, 
                           freq_MHz, 
                           self.tag, 
                           chunk_start_time=chunk_start_time, 
                           microsecond_correction=microsecond_correction,
                           spectrum_type="amplitude")
    
    def __get_final_sweep_previous_chunk(self, previous_chunk: SPECTREChunk) -> Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        # Read binary IQ data and header information from the previous chunk
        previous_sweep_IQ_data = previous_chunk.bin.read()
        _, prev_sweep_metadata = previous_chunk.hdr.read()
        prev_center_freqs, prev_num_samples = prev_sweep_metadata
        # Identify the first step index for the final sweep
        min_freq_step = np.min(prev_center_freqs)
        step_indices = np.where(prev_center_freqs == min_freq_step)[0]
        final_sweep_start_index = step_indices[-1] 

        # Extract metadata for the final sweep
        final_center_freqs = prev_center_freqs[final_sweep_start_index:]
        final_num_samples = prev_num_samples[final_sweep_start_index:]

        # Calculate the number of samples in full sweeps and extract the IQ data for the final sweep
        full_sweep_samples_count = len(previous_sweep_IQ_data) - np.sum(final_num_samples)
        final_sweep_IQ_data = previous_sweep_IQ_data[full_sweep_samples_count:]

        # Verify the number of IQ samples matches the expected total
        expected_samples_count = np.sum(final_num_samples)
        actual_samples_count = len(final_sweep_IQ_data)

        if expected_samples_count != actual_samples_count:
            raise ValueError(
                f"Mismatch in sample count! Expected: {expected_samples_count}, Actual: {actual_samples_count}"
            )

        final_sweep_metadata = (final_center_freqs, final_num_samples)
        return final_sweep_IQ_data, final_sweep_metadata
    


    def __get_corrected_timing(self, millisecond_correction: int, 
                               sweep_metadata: Tuple[np.ndarray, np.ndarray]) -> Tuple[str, int]:
        # extract the number of samples to prepend
        _, num_samples_to_prepend = sweep_metadata
        # Calculate the total number of samples to prepend
        total_samples_to_prepend = np.sum(num_samples_to_prepend)
        # Determine the sampling interval from the capture configuration
        sampling_interval = 1 / self.capture_config.get("samp_rate")
        # Calculate the elapsed seconds in the prepended samples
        elapsed_seconds = sampling_interval * total_samples_to_prepend
        # Compute the corrected chunk start datetime
        corrected_datetime = (self.chunk_start_datetime + 
                            timedelta(milliseconds=millisecond_correction) - 
                            timedelta(seconds=elapsed_seconds))
        # Format the corrected chunk start time
        corrected_start_time = datetime.strftime(corrected_datetime, CONFIG.default_time_format)
        # Calculate the corrected millisecond correction
        corrected_millisecond_correction = corrected_datetime.microsecond / 1000
        return corrected_start_time, corrected_millisecond_correction


    def __prepend_sweep_IQ_data(self, 
                         sweep_IQ_data: np.ndarray, 
                         sweep_IQ_data_to_prepend: np.ndarray) -> np.ndarray:
        return np.concatenate((sweep_IQ_data_to_prepend, sweep_IQ_data)) 
    

    def __prepend_sweep_metadata(self, 
                               sweep_metadata: Tuple[np.ndarray, np.ndarray],
                               sweep_metadata_to_prepend: Tuple[np.ndarray, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        
        center_frequencies, num_samples = sweep_metadata
        center_frequencies_to_prepend, num_samples_to_prepend = sweep_metadata_to_prepend
        # if a step from the previous chunk has bled over to the current chunk
        # (in other words, *final* center frequency in the previous chunk is equal to the *first* center freuqency of the current chunk)
        if center_frequencies_to_prepend[-1] == center_frequencies[0]:
            # truncate the center frequencies to prepend (so to avoid a duplicated step)
            center_frequencies_to_prepend = center_frequencies_to_prepend[:-1]
            # sum the number of samples and truncate accordingly
            num_samples[0] += num_samples_to_prepend[-1]
            num_samples_to_prepend = num_samples_to_prepend[:-1]
        # otherwise, the first sample of the new chunk is a completely new step, so there is no truncation required
        else:
            pass
        
        center_frequencies = np.concatenate((center_frequencies_to_prepend, center_frequencies))
        num_samples = np.concatenate((num_samples_to_prepend, num_samples))
        return center_frequencies, num_samples


    def __do_STFFT(self, 
                   sweep_IQ_data: np.ndarray, 
                   center_frequencies: np.ndarray, 
                   num_samples: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Initialize STFFT related parameters.
        self.window = self.__fetch_window()
        self.window_size = self.capture_config.get("window_size")
        self.samp_rate = self.capture_config.get("samp_rate")
        STFFT_kwargs = self.capture_config.get("STFFT_kwargs")
        self.SFT = ShortTimeFFT(self.window, fs=self.samp_rate, fft_mode="centered", **STFFT_kwargs)
        # compute sweep properties which define the stepped spectrogram shape
        self.num_steps_per_sweep = self.__compute_num_steps_per_sweep(center_frequencies)
        self.num_full_sweeps = self.__compute_num_full_sweeps(center_frequencies)
        self.num_frequencies_per_step = self.capture_config.get("window_size")
        self.num_max_slices_in_step = self.__compute_num_max_slices_in_step(num_samples)
        # compute the stepped spectrogram
        stepped_dynamic_spectra = self.__compute_stepped_dynamic_spectra(sweep_IQ_data, num_samples)
        # and average the steps totally in time
        stepped_dynamic_spectra = self.__average_steps_totally_in_time(stepped_dynamic_spectra)

        # build the time seconds array
        time_seconds = self.__compute_time_seconds(num_samples)
        # assign physical frequencies to the spectral components [MHz]
        freq_MHz = self.__compute_freq_MHz(center_frequencies) 
        # stitch together the swept spectrogram based on the stepped spectrogram
        dynamic_spectra = self.__compute_swept_dynamic_spectra(stepped_dynamic_spectra)

        return time_seconds, freq_MHz, dynamic_spectra


    def __fetch_window(self) -> np.ndarray:
        """
        Fetch and construct the window function for STFFT based on the capture configuration.
        """
        window_type = self.capture_config.get('window_type')
        window_kwargs = self.capture_config.get('window_kwargs')
        window_params = (window_type, *window_kwargs.values())
        window_size = self.capture_config.get('window_size')
        return get_window(window_params, window_size)


    def __compute_stepped_dynamic_spectra(self, sweep_IQ_data: np.ndarray, num_samples: np.ndarray) -> np.ndarray:
        """
        Compute the stepped dynamic spectra by performing STFFT on each step of the IQ data.
        """
        stepped_dynamic_spectra = np.empty((self.num_full_sweeps, 
                                                 self.num_steps_per_sweep, 
                                                 self.num_frequencies_per_step, 
                                                 self.num_max_slices_in_step))
        stepped_dynamic_spectra.fill(np.nan)

        global_step_index = 0
        start_index = 0
        for sweep_index in range(self.num_full_sweeps):
            for step_index in range(self.num_steps_per_sweep):
                num_samples_in_step = num_samples[global_step_index]
                end_index = start_index + num_samples_in_step
                num_slices_this_step = self.SFT.upper_border_begin(num_samples_in_step)[1]
                complex_spectra = self.SFT.stft(sweep_IQ_data[start_index:end_index], p0=0, p1=num_slices_this_step)
                dynamic_spectra = np.abs(complex_spectra)
                stepped_dynamic_spectra[sweep_index, step_index, :, 0:num_slices_this_step] = dynamic_spectra
                start_index = end_index
                global_step_index += 1

        return stepped_dynamic_spectra

    def __average_steps_totally_in_time(self, stepped_dynamic_spectra: np.ndarray) -> np.ndarray:
        # Average the stepped dynamic spectra in time.
        # Don't average the first slice (as it is affected by windowing artefacts)
        return np.nanmean(stepped_dynamic_spectra[..., 1:], axis=-1)
    


    def __compute_time_seconds(self, num_samples: np.ndarray) -> np.ndarray:
        # the data from each sweep get's mapped to a single spectrogram. We will assign this (by convention)
        # to whatever time is associated with the floored "middle" sample in the sweep.
        # in this we assume that each sample is produced at the input sample rate 
        # (an approximation as we ignore latency during API calls that return the frequency)

        # initialise an array to hold the assigned sample indices to each sweep
        assigned_sample_indices = []
        # initialise a variable to hold the cumulative samples processed in the loop
        # this is an internal variable used to infer the assigned sample for each sweep
        # in particular, for a particular sweep (say the "current" sweep):
        # assigned_index = total_samples_in_previous_sweeps + floor(total_samples_current_sweep/2)
        cumulative_samples = 0

        # iterate through each sweep
        for sweep_index in range(self.num_full_sweeps):
            # Calculate the step indices for the current sweep
            start_step = sweep_index * self.num_steps_per_sweep
            end_step = (sweep_index + 1) * self.num_steps_per_sweep
            # Sum the number of samples in the current sweep
            samples_in_sweep = np.sum(num_samples[start_step:end_step])
            # Determine the midpoint sample index of the current sweep
            midpoint_sample_index = cumulative_samples + floor(samples_in_sweep / 2)
            # prepend the midpoint sample index to the list
            assigned_sample_indices.append(midpoint_sample_index)
            # Update the cumulative sample count
            cumulative_samples += samples_in_sweep

        # Compute the time in seconds for each assigned sample index
        sampling_interval = 1 / self.samp_rate
        # and compute and return the time in seconds assigned to each sweep (or equivalently, the spectrum for that sweep)
        return np.array(assigned_sample_indices) * sampling_interval

    

    def __compute_freq_MHz(self, center_frequencies: np.ndarray) -> np.ndarray:
        freq_MHz = np.empty(self.num_steps_per_sweep * self.window_size)
        unique_center_frequencies = np.unique(center_frequencies)
        for i, center_frequency in enumerate(unique_center_frequencies):
            lower_index_bound = i*self.window_size
            upper_index_bound = (i+1)*self.window_size
            freq_Hz = (self.SFT.f + center_frequency)
            freq_MHz[lower_index_bound:upper_index_bound] = freq_Hz / 1e6
        return freq_MHz
    

    def __compute_swept_dynamic_spectra(self, stepped_dynamic_spectra: np.ndarray) -> np.ndarray:
        # Compute the final swept dynamic spectra from the averaged stepped spectra.
        num_sweeps = stepped_dynamic_spectra.shape[0]
        num_swept_spectral_components = stepped_dynamic_spectra.shape[1] * stepped_dynamic_spectra.shape[2]
        swept_dynamic_spectra = stepped_dynamic_spectra.reshape((num_sweeps, num_swept_spectral_components))
        return np.moveaxis(swept_dynamic_spectra, 0, 1)
    

    # Helper methods to compute parameters (unchanged for brevity)
    def __compute_num_steps_per_sweep(self, center_frequencies: np.ndarray) -> int:
        min_frequency = np.min(center_frequencies)
        step_indices_of_min_frequency = np.where(center_frequencies == min_frequency)[0]
        unique_num_steps_in_sweep = np.unique(np.diff(step_indices_of_min_frequency))
        if len(unique_num_steps_in_sweep) != 1:
            raise ValueError(f"Unexpected error, irregular step count per sweep!")
        return int(unique_num_steps_in_sweep[0])


    def __compute_num_full_sweeps(self, center_frequencies: np.ndarray) -> int:
        # Since the number of each samples in each step is variable, we only know a sweep is complete
        # when there is a sweep after it. So we can define the total number of *full* sweeps as the number of 
        # (freq_max, freq_min) pairs in center_frequencies. Since at the sweep boundaries this is the only time
        # that the frequency step decreases, we can compute the number of full sweeps by counting the numbers of negative
        # values in np.diff(center_frequencies)
        step_diffs = np.diff(center_frequencies)
        negative_diffs = step_diffs[step_diffs<0]
        return len(negative_diffs)


    def __compute_num_max_slices_in_step(self, num_samples: np.ndarray) -> int:
        num_max_samples_in_step = np.max(num_samples)
        return self.SFT.upper_border_begin(num_max_samples_in_step)[1]
    

