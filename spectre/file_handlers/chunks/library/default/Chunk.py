# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from typing import Tuple
from scipy.signal import ShortTimeFFT, get_window
import matplotlib.pyplot as plt

from spectre.file_handlers.chunks.SPECTREChunk import SPECTREChunk
from spectre.file_handlers.chunks.chunk_register import register_chunk
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.file_handlers.chunks.library.default.BinChunk import BinChunk
from spectre.file_handlers.chunks.library.default.FitsChunk import FitsChunk
from spectre.file_handlers.chunks.library.default.HdrChunk import HdrChunk

@register_chunk('default')
class Chunk(SPECTREChunk):
    def __init__(self, chunk_start_time: str, tag: str):
        super().__init__(chunk_start_time, tag) 
        
        self.add_file(BinChunk(self.chunk_parent_path, self.chunk_name))
        self.add_file(FitsChunk(self.chunk_parent_path, self.chunk_name))
        self.add_file(HdrChunk(self.chunk_parent_path, self.chunk_name))


    def build_spectrogram(self) -> Spectrogram:
        # fetch the raw IQ sample receiver output from the binary file
        IQ_data = self.read_file("bin")
        # and the millisecond correction from the accompanying header file
        millisecond_correction = self.read_file("hdr")

        # convert the millisecond correction to microseconds
        microsecond_correction = millisecond_correction * 1000

        # do the short time fft
        time_seconds, freq_MHz, dynamic_spectra = self.__do_STFFT(IQ_data)

        # convert all arrays to the standard type
        time_seconds = np.array(time_seconds, dtype = 'float32')
        freq_MHz = np.array(freq_MHz, dtype = 'float32')
        dynamic_spectra = np.array(dynamic_spectra, dtype = 'float32')

        return Spectrogram(dynamic_spectra, 
                time_seconds, 
                freq_MHz, 
                self.tag, 
                chunk_start_time = self.chunk_start_time, 
                microsecond_correction = microsecond_correction,
                spectrum_type="amplitude")

    
    def __fetch_window(self) -> np.ndarray:
        # fetch the window params and get the appropriate window
        window_type = self.capture_config.get('window_type')
        window_kwargs = self.capture_config.get('window_kwargs')
        ## note the implementation ignores the keys by necessity, due to the scipy implementation of get_window
        window_params = (window_type, *window_kwargs.values())
        window_size = self.capture_config.get('window_size')
        return get_window(window_params, window_size)
    

    def __do_STFFT(self, IQ_data: np.array) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        '''
        For reference: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.ShortTimeFFT.html
        '''
        # fetch the window
        w = self.__fetch_window()
        # find the number of samples 
        num_samples = len(IQ_data)
        # fetch the sample rate
        samp_rate = self.capture_config.get('samp_rate')
        # fetch the STFFT kwargs
        STFFT_kwargs = self.capture_config.get('STFFT_kwargs')

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
        center_freq = self.capture_config.get('center_freq', 0)
        # build the frequency array
        frequency_array = SFT.f + center_freq # Hz
        # convert the frequency array to MHz
        freq_MHz = frequency_array / 10**6

        return time_seconds, freq_MHz, dynamic_spectra




