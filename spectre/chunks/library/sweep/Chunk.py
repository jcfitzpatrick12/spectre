# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from typing import Tuple
from scipy.signal import ShortTimeFFT, get_window
import matplotlib.pyplot as plt
from math import floor

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
        
        # Initialize shared attributes with default values
        self.window = None
        self.SFT = None
        self.num_steps_per_sweep = None
        self.num_full_sweeps = None
        self.num_frequencies_per_step = None
        self.num_max_slices_in_step = None

    def build_spectrogram(self) -> Spectrogram:
        # Build and return the spectrogram for the chunk
        IQ_data = self.bin.read()
        millisecond_correction, center_frequencies, num_samples = self.hdr.read()
        microsecond_correction = millisecond_correction * 1000

        time_seconds, freq_MHz, dynamic_spectra = self.__do_STFFT(IQ_data, 
                                                                  center_frequencies, 
                                                                  num_samples)

        time_seconds = np.array(time_seconds, dtype='float64')
        freq_MHz = np.array(freq_MHz, dtype='float64')
        dynamic_spectra = np.array(dynamic_spectra, dtype='float64')

        return Spectrogram(dynamic_spectra, 
                           time_seconds, 
                           freq_MHz, 
                           self.tag, 
                           chunk_start_time=self.chunk_start_time, 
                           microsecond_correction=microsecond_correction,
                           spectrum_type="amplitude")

    def __do_STFFT(self, 
                   IQ_data: np.ndarray, 
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
        self.num_full_sweeps = self.__compute_num_full_sweeps(center_frequencies, self.num_steps_per_sweep)
        self.num_frequencies_per_step = self.capture_config.get("window_size")
        self.num_max_slices_in_step = self.__compute_num_max_slices_in_step(num_samples)
        # compute the stepped spectrogram
        stepped_dynamic_spectra = self.__compute_stepped_dynamic_spectra(IQ_data, num_samples)
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


    def __compute_stepped_dynamic_spectra(self, IQ_data: np.ndarray, num_samples: np.ndarray) -> np.ndarray:
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
                complex_spectra = self.SFT.stft(IQ_data[start_index:end_index], p0=0, p1=num_slices_this_step)
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
            # Append the midpoint sample index to the list
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


    def __compute_num_full_sweeps(self, center_frequencies: np.ndarray, num_steps_per_sweep) -> int:
        num_steps = len(center_frequencies)
        return floor(num_steps / num_steps_per_sweep)


    def __compute_num_max_slices_in_step(self, num_samples: np.ndarray) -> int:
        num_max_samples_in_step = np.max(num_samples)
        return self.SFT.upper_border_begin(num_max_samples_in_step)[1]
