# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Callable, Any, Tuple

import numpy as np

from spectre.file_handlers.json_configs import CaptureConfigHandler
from spectre.spectrograms.spectrogram import Spectrogram
from spectre.exceptions import ModeNotFoundError


def add_builder(test_mode: str):
    def decorator(func: Callable):
        def wrapper(self, *args, **kwargs):
            self.builders[test_mode] = func
            return func(*args, **kwargs)
        return wrapper
    return decorator

class _AnalyticalFactory:
    def __init__(self):
        self._builders: dict[str, Callable] = {}
        self._test_modes = list(self.builders.keys())


    @property
    def builders(self) -> dict[str, Callable]:
        return self._builders
    

    @property
    def test_modes(self) -> list[str]:
        return self._test_modes
    

    def get_spectrogram(self, 
                        test_mode: str, 
                        spectrogram_shape: tuple, 
                        capture_config: dict[str, Any]) -> Spectrogram:
        builder_method = self.builders.get(test_mode)
        if builder_method is None:
            raise ModeNotFoundError(f"Test mode not found. Expected one of {self.test_modes}, but received {test_mode}")
        return builder_method(spectrogram_shape, capture_config)
    

    @add_builder("cosine_signal_1")
    def cosine_signal_1(self, 
                        spectrogram_shape: tuple,
                        capture_config: dict[str, Any]) -> Spectrogram:

        # retrieve the parameters in the capture config which are required 
        # to build the analytical spectrogram.
        window_size = capture_config['window_size']
        samp_rate = capture_config['samp_rate'] 
        amplitude = capture_config['amplitude'] 
        frequency = capture_config['frequency']
        hop = capture_config['STFFT_kwargs']['hop']

        # get the requested shape of the output spectrogram
        num_frequencies = spectrogram_shape[0]
        num_times = spectrogram_shape[1]

        # ensure it is consistent with the capture config
        if window_size != num_frequencies:
            raise ValueError((f"Expected the number of frequencies to be the same as the window size. "
                              f"Got {num_frequencies}, but the window size is {window_size}"))

        # a defines the ratio of the sampling rate to the frequency of the synthetic signal
        a = int(samp_rate / frequency)

        # p is effectively the "number of sampled periods"
        # which can be found equal to the ratio of window_size to a
        p = int(window_size / a)

        # for the case of cosine-signal-1, the spectrogram
        # should be constant in time so we will build one spectrum, 
        # then use that to populate the spectrogram.
        spectrum = np.empty(num_frequencies)
        derived_spectral_amplitude = amplitude * window_size / 2
        spectrum[p] = derived_spectral_amplitude
        spectrum[window_size - p] = derived_spectral_amplitude

        # analytical solution is derived for 0 <= k <= N-1 DFT summation indexing
        # so, we need to fftshift the array to align the slices to the naturally
        # ordered frequency array (-ve -> +ve for increasing indices from 0 -> N-1)
        spectrum= np.fft.fftshift(spectrum)

        
        # fill the analytical spectra identically with the common derived
        # spectrum.
        analytical_dynamic_spectra = np.empty(spectrogram_shape)
        analytical_dynamic_spectra = analytical_dynamic_spectra*spectrum[:, np.newaxis]   

        # assign physical times to each of the spectrum
        sampling_interval = ( 1 / samp_rate )
        times = np.array([tau*hop*sampling_interval for tau in range(num_times)])

        # assign physical frequencies to each spectrum
        frequencies = np.fft.fftfreq(num_frequencies, sampling_interval)
        frequencies = np.fft.fftshift(frequencies)

        return Spectrogram(analytical_dynamic_spectra,
                           times,
                           frequencies,
                           'analytically-derived-spectrogram',
                           spectrum_type = "amplitude")


def get_analytical_spectrogram(test_mode: str,
                               spectrogram_shape: Tuple[int, int, int],
                               capture_config: dict[str, Any]) -> Spectrogram:
    factory = _AnalyticalFactory()
    return factory.get_spectrogram(test_mode, 
                                   spectrogram_shape,
                                   capture_config)


def _close_enough(ar: np.ndarray, ar_comparison: np.ndarray) -> bool:
    return np.all(np.isclose(ar, ar_comparison, atol=1e-4))


def validate_analytically(spectrogram: Spectrogram,
                          capture_config: dict) -> None:
    
    # check that capture config was created by a test receiver
    receiver_name, test_mode = capture_config["receiver"], capture_config["mode"]
    if receiver_name != "test":
        raise ValueError(f"Expected a capture config created by a test receiver, but found {receiver_name}")
    
    # build the analyticaly derived solution
    analytical_spectrogram = get_analytical_spectrogram(test_mode,
                                                        spectrogram.dynamic_spectra.shape,
                                                        capture_config)
    
    # compare results
    if not _close_enough(analytical_spectrogram.dynamic_spectra, 
                         spectrogram.dynamic_spectra):
        raise ValueError(f"Analytical validation has failed! Mismatch in dynamic spectra.")
    
    if not _close_enough(analytical_spectrogram.times,
                         spectrogram.times):
        raise ValueError(f"Analytical validation has failed! Mismatch in times.")
    
    if not _close_enough(analytical_spectrogram.frequencies,
                         spectrogram.frequencies):
        raise ValueError(f"Analytical validation has failed! Mismatch in frequencies.")
