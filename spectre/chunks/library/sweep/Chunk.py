# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from typing import Tuple
from math import floor
from scipy.signal import ShortTimeFFT, get_window

from spectre.chunks.BaseChunk import BaseChunk
from spectre.chunks.chunk_register import register_chunk
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.chunks.library.default.ChunkFits import ChunkFits # same fits handling class as "default" chunks
from spectre.chunks.library.sweep.ChunkBin import ChunkBin


@register_chunk('sweep')
class Chunk(BaseChunk):
    def __init__(self, chunk_start_time: str, tag: str):
        super().__init__(chunk_start_time, tag) 
        self.bin = ChunkBin(chunk_start_time, tag)
        self.fits = ChunkFits(chunk_start_time, tag)


    def build_spectrogram(self) -> Spectrogram: 
        # read the raw binary data
        millisecond_correction, frequency_tagged_IQ_data = self.bin.read()
        # infer the total number of samples
        num_total_samples = np.shape(frequency_tagged_IQ_data)[0]

        # compute the sweep attributes required to create the spectrogram
        self.set_sweep_attrs(num_total_samples)

        #truncate the tagged IQ data so to only include full sweeps
        frequency_tagged_IQ_data = frequency_tagged_IQ_data[:self.truncation_index]

        # reshape to emphasise stepped structure
        samples_per_step = self.capture_config.get("samples_per_step")
        frequency_tagged_IQ_data = np.reshape(frequency_tagged_IQ_data,
                                              (self.num_full_sweeps, 
                                               self.num_steps_in_one_sweep, 
                                               samples_per_step,
                                               3))
        
        # separate the tagged data into it's components
        tagged_frequencies = frequency_tagged_IQ_data[...,0]
        IQ_data = frequency_tagged_IQ_data[...,1] + 1j*frequency_tagged_IQ_data[...,2]


        stepped_dynamic_spectra, stepped_freq_MHz = self.compute_stepped_arrays(tagged_frequencies,
                                                                                IQ_data)
        stitched_dynamic_spectra, stitched_freq_MHz = self.compute_stitched_arrays(stepped_dynamic_spectra, 
                                                                                   stepped_freq_MHz)
        stitched_time_seconds = self.compute_stitched_time_seconds()

        return Spectrogram(
            stitched_dynamic_spectra,
            stitched_time_seconds,
            stitched_freq_MHz,
            self.tag,
            self.chunk_start_time,
            units='amplitude',
            microsecond_correction = millisecond_correction * 1000
        )
    

    def set_sweep_attrs(self, num_total_samples: int) -> None:
        # unpack relevant variables from the capture config
        samples_per_step = self.capture_config.get("samples_per_step")
        min_freq = self.capture_config.get("min_freq")
        max_freq = self.capture_config.get("max_freq")
        freq_step = self.capture_config.get("freq_step")
        window_size = self.capture_config.get('window_size')
        samp_rate = self.capture_config.get("samp_rate")
        STFFT_kwargs = self.capture_config.get("STFFT_kwargs")

        # create an instance of the ShortTimeFFT class
        w = self.fetch_window(self.capture_config)
        samp_rate = self.capture_config.get("samp_rate")
        STFFT_kwargs = self.capture_config.get("STFFT_kwargs")
        SFT = ShortTimeFFT(w, fs=samp_rate, fft_mode='centered', **STFFT_kwargs)
        p1 = SFT.upper_border_begin(samples_per_step)[1]

        # compute the attributes
        num_steps_in_one_sweep = floor((max_freq-min_freq)/freq_step)
        num_frequencies_per_step = window_size
        num_slices_per_step = p1
        num_samples_full_sweep = samples_per_step*num_steps_in_one_sweep
        num_full_sweeps = floor(num_total_samples/num_samples_full_sweep)
        num_total_steps = num_full_sweeps * num_steps_in_one_sweep
        num_stitched_frequencies = num_frequencies_per_step * num_steps_in_one_sweep
        num_stitched_times = num_slices_per_step*num_full_sweeps
        num_extra_samples = num_total_samples % num_samples_full_sweep
        truncation_index = num_total_samples - num_extra_samples

        # set the attributes
        self.SFT = SFT
        self.p0 = 0
        self.p1 = p1
        self.num_total_samples = num_total_samples
        self.num_steps_in_one_sweep = num_steps_in_one_sweep
        self.num_samples_full_sweep = num_samples_full_sweep
        self.num_total_steps = num_total_steps
        self.num_frequencies_per_step = num_frequencies_per_step
        self.num_full_sweeps = num_full_sweeps  
        self.num_slices_per_step = num_slices_per_step 
        self.num_stitched_frequencies = num_stitched_frequencies
        self.num_stitched_times = num_stitched_times
        self.num_extra_samples = num_extra_samples
        self.truncation_index = truncation_index
        return
        

    def compute_stepped_arrays(self, 
                               tagged_frequencies: np.ndarray,
                               IQ_data: np.ndarray
                               ) -> Tuple[np.ndarray, np.ndarray]:
        
        # prime an array to hold the non-stitched dynamic spectra
        stepped_dynamic_spectra = np.empty((
            self.num_full_sweeps,
            self.num_steps_in_one_sweep,
            self.num_frequencies_per_step,
            self.num_slices_per_step
        ))

        # prime an array to hold the non-stitched frequency and time arrays
        stepped_freq_MHz = np.empty((
            self.num_full_sweeps,
            self.num_steps_in_one_sweep,
            self.num_frequencies_per_step,
        ))

        # populate the stepped arrays
        for sweep_index in range(0, self.num_full_sweeps):
            for step_index in range(0, self.num_steps_in_one_sweep):

                # checked the tagged_frequencies
                unique_center_freqs = np.unique(tagged_frequencies[sweep_index, step_index])
                if len(unique_center_freqs) != 1:
                    raise ValueError(f"Unexpected error! We should only have one unique center frequency per step.")
                
                # extract the (ensured unique) center frequency for this step
                center_freq_this_step = unique_center_freqs[0]

                # extract the IQ data for this step
                IQ_data_this_step = IQ_data[sweep_index, step_index]

                # do the STFFT
                complex_spectra = self.SFT.stft(IQ_data_this_step, p0=self.p0, p1=self.p1)
                dynamic_spectra = np.abs(complex_spectra)
                
                # build the stepped frequency and time arrays
                frequency_array = self.SFT.f + center_freq_this_step # Hz
                freq_MHz = frequency_array / 1e6

                # populate the stepped spectra arrays
                stepped_dynamic_spectra[sweep_index, step_index] = dynamic_spectra
                stepped_freq_MHz[sweep_index, step_index] = freq_MHz

        return stepped_dynamic_spectra, stepped_freq_MHz


    def compute_stitched_arrays(self, stepped_dynamic_spectra: np.ndarray, 
                                      stepped_freq_MHz: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        # construct the stitched arrays
        stitched_dynamic_spectra = np.empty((
            self.num_stitched_frequencies,
            self.num_stitched_times
        ))

        stitched_freq_MHz = np.empty((
            self.num_stitched_frequencies
        ))

        # populate the stitched arrays
        for sweep_index in range(0, self.num_full_sweeps):
            for step_index in range(0, self.num_steps_in_one_sweep):
                t_l = sweep_index*self.num_slices_per_step
                t_u = (sweep_index+1)*self.num_slices_per_step
                f_l = step_index*self.num_frequencies_per_step
                f_u = (step_index+1)*self.num_frequencies_per_step

                # populate the stitched dynamic spectra
                stitched_dynamic_spectra[f_l:f_u, t_l:t_u] = stepped_dynamic_spectra[sweep_index, step_index]
       
                # populate the frequency array
                stitched_freq_MHz[f_l:f_u] = stepped_freq_MHz[sweep_index, step_index]

        return stitched_dynamic_spectra, stitched_freq_MHz


    def compute_stitched_time_seconds(self) -> np.ndarray:
        samp_rate = self.capture_config.get("samp_rate")
        total_elapsed_time = self.num_total_samples * 1/samp_rate
        return np.linspace(0, total_elapsed_time, self.num_full_sweeps*self.num_slices_per_step)
    

    def fetch_window(self, capture_config: dict) -> np.ndarray:
        # fetch the window params and get the appropriate window
        window_type = capture_config.get('window_type')
        window_kwargs = capture_config.get('window_kwargs')
        ## note the implementation ignores the keys by necessity, due to the scipy implementation of get_window
        window_params = (window_type, *window_kwargs.values())
        window_size = capture_config.get('window_size')
        w = get_window(window_params, window_size)
        return w
    