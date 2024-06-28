# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from typing import Tuple
from scipy.signal import ShortTimeFFT, get_window
import matplotlib.pyplot as plt
from math import floor

from spectre.chunks.BaseChunk import BaseChunk
from spectre.chunks.chunk_register import register_chunk
from spectre.json_config.CaptureConfigHandler import CaptureConfigHandler
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
        # load the capture config for the current tag
        capture_config_handler = CaptureConfigHandler(self.tag)
        capture_config = capture_config_handler.load_as_dict()
        samples_per_step = capture_config.get("samples_per_step")
        min_freq = capture_config.get("min_freq")
        max_freq = capture_config.get("max_freq")
        freq_step = capture_config.get("freq_step")
        samp_rate = capture_config.get('samp_rate')
        STFFT_kwargs = capture_config.get('STFFT_kwargs')
        window_size = capture_config.get('window_size')


        # derived quantities
        num_unique_center_freqs = floor((max_freq-min_freq)/freq_step)
        len_full_sweep = samples_per_step*num_unique_center_freqs
        # build the spectra array



        # extract the millisecond correction and frequency tagged IQ data
        millisecond_correction, frequency_tagged_IQ_data = self.bin.read()

        # truncate the data s.t. we have only entirely complete sweeps
        total_samples = np.shape(frequency_tagged_IQ_data)[0]
        remainder = total_samples % len_full_sweep
        num_full_sweeps = int(total_samples/len_full_sweep)
        final_index = total_samples - remainder 
        frequency_tagged_IQ_data = frequency_tagged_IQ_data[:final_index]

        # reshape over full sweeps
        frequency_tagged_IQ_data = frequency_tagged_IQ_data.reshape((num_full_sweeps, len_full_sweep, 3))

        # fetch the window
        w = self.fetch_window(capture_config)
        # perform the short time FFT (specifying explicately keywords centered)
        SFT = ShortTimeFFT(w, fs=samp_rate, fft_mode='centered', **STFFT_kwargs)

        # set p0=0, since by convention in the STFFT docs, p=0 corresponds to the slice centred at t=0
        p0=0
        # set p1=p_ub, the index of the first slice where the "midpoint" of the window is still inside the signal
        p_ub = SFT.upper_border_begin(samples_per_step)[1]
        p1=p_ub

        # hack in the exact shape of the array
        stitched_spectra = np.empty((window_size*num_unique_center_freqs, 1495*num_full_sweeps))
        # loop over the full sweeps
        for sweep_index in range(0,num_full_sweeps):
            this_sweep = frequency_tagged_IQ_data[sweep_index]
            IQ_data = this_sweep[:,1:]
            center_freqs = this_sweep[:,0]
            # loop over each step within a particular sweep
            for i in range(0, num_unique_center_freqs):
                # deduce the exact indices of the step
                start_index = i*samples_per_step
                end_index = (i+1)*samples_per_step
                # truncate the data
                IQ_data_at_step = IQ_data[start_index:end_index]
                center_freqs_at_step = center_freqs[start_index: end_index]

                # convert the IQ_data to a complex array
                IQ_data_at_step = self.convert_to_complex(IQ_data_at_step)

                # do the STFFT
                signal_spectra = SFT.stft(IQ_data_at_step, p0=p0, p1=p1)  # perform the STFT (no scaling)
                # take the magnitude of the output
                dynamic_spectra = np.abs(signal_spectra)
                # fetch the center_freq (if not specified, defaults to zero)
                center_freq = np.unique(center_freqs_at_step)[0]
                # build the frequency array
                frequency_array = SFT.f + center_freq # Hz

                freq_ind_lower_bound = sweep_index*window_size
                freq_ind_upper_bound = (sweep_index+1)*window_size

                time_index_lower_bound = sweep_index*(1495)
                time_index_upper_bound = (sweep_index+1)*1495
                stitched_spectra[freq_ind_lower_bound:freq_ind_upper_bound,time_index_lower_bound:time_index_upper_bound]

        
        exit()
        ## forget about time for now, just use indices ... 
        return
    

    def fetch_window(self, capture_config: dict) -> np.ndarray:
        # fetch the window params and get the appropriate window
        window_type = capture_config.get('window_type')
        window_kwargs = capture_config.get('window_kwargs')
        ## note the implementation ignores the keys by necessity, due to the scipy implementation of get_window
        window_params = (window_type, *window_kwargs.values())
        window_size = capture_config.get('window_size')
        w = get_window(window_params, window_size)
        return w


    def convert_to_complex(self, array: np.ndarray) -> np.ndarray:
        # Combine the real and imaginary parts into a complex array
        complex_array = array[:, 0] + 1j * array[:, 1]
        return complex_array