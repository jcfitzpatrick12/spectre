# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np

from spectre.spectrogram.Spectrogram import Spectrogram

class AnalyticalSpectrogramFactory:
    def __init__(self,):
        self.builder_methods = {
            "cosine-signal-1": self.cosine_signal_1
        }
        self.test_modes = list(self.builder_methods.keys())

    def get_spectrogram(self, test_mode: str, shape: tuple, capture_config: dict) -> Spectrogram:
        builder_method = self.builder_methods.get(test_mode)
        if builder_method is None:
            raise ValueError(f"Invalid test mode. Expected one of {self.test_modes}, but received {test_mode}.")
        S = builder_method(shape, capture_config)
        return S
    
    def cosine_signal_1(self, 
                            shape: tuple,
                            capture_config: dict
                             ):
        
        window_size = capture_config['window_size']
        samp_rate = capture_config['samp_rate'] 
        amplitude = capture_config['amplitude'] 
        frequency = capture_config['frequency']
        hop = capture_config['STFFT_kwargs']['hop']
        
        shape_type = type(shape)
        if shape_type != tuple:
            raise TypeError(f"\"shape\" must be set as a tuple. Received {shape_type}")

        # a defines the ratio of the sampling rate to the frequency of the synthetic signal
        a = int(samp_rate / frequency)
        # p is the "number of sampled periods"
        # which can be found equal to the ratio of window_size to a
        p = int(window_size / a)
        # infer the number of frequency samples
        num_frequency_samples = shape[0]
        num_time_samples = shape[1]

        spectral_slice = np.zeros(num_frequency_samples)
        derived_spectral_amplitude = amplitude * window_size / 2
        spectral_slice[p] = derived_spectral_amplitude
        spectral_slice[window_size - p] = derived_spectral_amplitude
        # analytical solution is derived for 0 <= k <= N-1 DFT summation indexing
        # so, we need to fftshift the array to align the slices to the naturally
        # ordered frequency array (-ve -> +ve for increasing indices from 0 -> N-1)
        spectral_slice = np.fft.fftshift(spectral_slice)

        # build the analytical spectrogram
        analytical_dynamic_spectra = np.ones(shape)
        analytical_dynamic_spectra = analytical_dynamic_spectra*spectral_slice[:, np.newaxis]   

        time_seconds = np.array([tau*hop*(1/samp_rate) for tau in range(num_time_samples)])

        freq_MHz = np.fft.fftfreq(num_frequency_samples, 1/samp_rate)*1e-6
        freq_MHz = np.fft.fftshift(freq_MHz)

        S = Spectrogram(analytical_dynamic_spectra,
                                   time_seconds,
                                   freq_MHz,
                                   'analytically-derived-spectrogram',
                                   spectrum_type = "amplitude",)
        
        return S
