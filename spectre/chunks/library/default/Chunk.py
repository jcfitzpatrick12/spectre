# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from typing import Tuple
from scipy.signal import ShortTimeFFT, get_window
import matplotlib.pyplot as plt

from spectre.chunks.BaseChunk import BaseChunk
from spectre.chunks.chunk_register import register_chunk
from spectre.json_config.CaptureConfigHandler import CaptureConfigHandler
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.chunks.library.default.ChunkBin import ChunkBin
from spectre.chunks.library.default.ChunkFits import ChunkFits


@register_chunk('default')
class Chunk(BaseChunk):
    def __init__(self, chunk_start_time: str, tag: str):
        super().__init__(chunk_start_time, tag) 

        self.bin = ChunkBin(chunk_start_time, tag)
        self.fits = ChunkFits(chunk_start_time, tag)


    def build_spectrogram(self) -> Spectrogram:
        
        if not self.bin.exists():
            raise FileNotFoundError(f"Cannot build spectrogram, {self.bin.get_path()} does not exist.")
        # fetch the IQ data
        millisecond_correction, IQ_data = self.bin.read()
        # load the capture config for the current tag
        capture_config_handler = CaptureConfigHandler(self.tag)
        capture_config = capture_config_handler.load_as_dict()

        # do the short time fft
        time_seconds, freq_MHz, dynamic_spectra = self.do_STFFT(IQ_data, capture_config)

        # convert all arrays to the standard type
        time_seconds = np.array(time_seconds, dtype = 'float64')
        freq_MHz = np.array(freq_MHz, dtype = 'float64')
        dynamic_spectra = np.array(dynamic_spectra, dtype = 'float64')

        return Spectrogram(dynamic_spectra, 
                time_seconds, 
                freq_MHz, 
                self.tag, 
                chunk_start_time = self.chunk_start_time, 
                units="amplitude",
                millisecond_correction = millisecond_correction)

    
    def fetch_window(self, capture_config: dict) -> np.ndarray:
        # fetch the window params and get the appropriate window
        window_type = capture_config.get('window_type')
        window_kwargs = capture_config.get('window_kwargs')
        ## note the implementation ignores the keys by necessity, due to the scipy implementation of get_window
        window_params = (window_type, *window_kwargs.values())
        window_size = capture_config.get('window_size')
        w = get_window(window_params, window_size)
        return w
    

    def do_STFFT(self, IQ_data: np.array, capture_config: dict) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        '''
        For reference: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.ShortTimeFFT.html
        '''
        # fetch the window
        w = self.fetch_window(capture_config)
        # find the number of samples 
        num_samples = len(IQ_data)
        # fetch the sample rate
        samp_rate = capture_config.get('samp_rate')
        # fetch the STFFT kwargs
        STFFT_kwargs = capture_config.get('STFFT_kwargs')

        # perform the short time FFT (specifying explicately keywords centered)
        SFT = ShortTimeFFT(w, fs=samp_rate, fft_mode='centered', **STFFT_kwargs)

        # set p0=0, since by convention in the STFFT docs, p=0 corresponds to the slice centred at t=0
        p0=0
        # set p1=p_ub, the index of the first slice where the "midpoint" of the window is still inside the signal
        p_ub = SFT.upper_border_begin(num_samples)[1]
        p1=p_ub
        
        signal_spectra = SFT.stft(IQ_data, p0=p0, p1=p1)  # perform the STFT (no scaling)
        # take the magnitude of the output
        dynamic_spectra = np.abs(signal_spectra)

        # build the time array
        time_seconds = SFT.t(num_samples, p0=0, p1=p1) # seconds

        # fetch the center_freq (if not specified, defaults to zero)
        center_freq = capture_config.get('center_freq', 0)
        # build the frequency array
        frequency_array = SFT.f + center_freq # Hz
        # convert the frequency array to MHz
        freq_MHz = frequency_array / 10**6

        return time_seconds, freq_MHz, dynamic_spectra




