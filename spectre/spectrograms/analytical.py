# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Callable
from dataclasses import dataclass

import numpy as np

from spectre.file_handlers.configs import CaptureConfig
from spectre.spectrograms.spectrogram import Spectrogram
from spectre.spectrograms.array_operations import is_close
from spectre.exceptions import ModeNotFoundError



@dataclass
class TestResults:
    # Whether the times array matches analytically
    times_validated: bool = False  
    # Whether the frequencies array matches analytically
    frequencies_validated: bool = False  
    # Maps each time to whether the corresponding spectrum matched analytically
    spectrum_validated: dict[float, bool] = None

    @property
    def num_validated_spectrums(self) -> int:
        """Counts the number of validated spectrums."""
        return sum(is_validated for is_validated in self.spectrum_validated.values())

    @property
    def num_invalid_spectrums(self) -> int:
        """Counts the number of spectrums that are not validated."""
        return len(self.spectrum_validated) - self.num_validated_spectrums


class _AnalyticalFactory:
    def __init__(self):
        self._builders: dict[str, Callable] = {
            "cosine-signal-1": self.cosine_signal_1,
            "tagged-staircase": self.tagged_staircase
        }
        self._test_modes = list(self.builders.keys())


    @property
    def builders(self) -> dict[str, Callable]:
        return self._builders
    

    @property
    def test_modes(self) -> list[str]:
        return self._test_modes
    

    def get_spectrogram(self, 
                        num_spectrums: int, 
                        capture_config: CaptureConfig) -> Spectrogram:
        """Get an analytical spectrogram based on a test receiver capture config.
        
        The anaytically derived spectrogram should be able to be fully determined
        by parameters in the corresponding capture config and the number of spectrums
        in the output spectrogram.
        """
        receiver_name, test_mode = capture_config['receiver'], capture_config['mode']

        if receiver_name != "test":
            raise ValueError(f"Input capture config must correspond to the test receiver")
        
        builder_method = self.builders.get(test_mode)
        if builder_method is None:
            raise ModeNotFoundError(f"Test mode not found. Expected one of {self.test_modes}, but received {test_mode}")
        return builder_method(num_spectrums, 
                              capture_config)
    

    def cosine_signal_1(self, 
                        num_spectrums: int,
                        capture_config: CaptureConfig) -> Spectrogram:
        # Extract necessary parameters from the capture configuration.
        window_size = capture_config['window_size']
        samp_rate = capture_config['samp_rate']
        amplitude = capture_config['amplitude']
        frequency = capture_config['frequency']
        hop = capture_config['STFFT_kwargs']['hop']

        # Calculate derived parameters a (sampling rate ratio) and p (sampled periods).
        a = int(samp_rate / frequency)
        p = int(window_size / a)

        # Create the analytical spectrum, which is constant in time.
        spectrum = np.zeros(window_size)
        derived_spectral_amplitude = amplitude * window_size / 2
        spectrum[p] = derived_spectral_amplitude
        spectrum[window_size - p] = derived_spectral_amplitude

        # Align spectrum to naturally ordered frequency array.
        spectrum = np.fft.fftshift(spectrum)

        # Populate the spectrogram with identical spectra.
        analytical_dynamic_spectra = np.ones((window_size, num_spectrums)) * spectrum[:, np.newaxis]

        # Compute time array.
        sampling_interval = 1 / samp_rate
        times = np.arange(num_spectrums) * hop * sampling_interval

        # compute the frequency array.
        frequencies = np.fft.fftshift(np.fft.fftfreq(window_size, sampling_interval))

        # Return the spectrogram.
        return Spectrogram(analytical_dynamic_spectra,
                           times,
                           frequencies,
                           'analytically-derived-spectrogram',
                           spectrum_type="amplitude")


    def tagged_staircase(self, 
                        num_spectrums: int,
                        capture_config: CaptureConfig) -> Spectrogram:
        # Extract necessary parameters from the capture configuration.
        window_size = capture_config['window_size']
        min_samples_per_step = capture_config['min_samples_per_step']
        max_samples_per_step = capture_config['max_samples_per_step']
        step_increment = capture_config['step_increment']
        samp_rate = capture_config['samp_rate']

        # Calculate step sizes and derived parameters.
        num_samples_per_step = np.arange(min_samples_per_step, max_samples_per_step + 1, step_increment)
        num_steps = len(num_samples_per_step)

        # Create the analytical spectrum, constant in time.
        spectrum = np.zeros(window_size * num_steps)
        for i in range(num_steps):
            spectrum[int(window_size/2) + i*window_size] = window_size * i

        # Populate the spectrogram with identical spectra.
        analytical_dynamic_spectra = np.ones((window_size * num_steps, num_spectrums)) * spectrum[:, np.newaxis]

        # Compute time array
        num_samples_per_sweep = sum(num_samples_per_step)
        midpoint_sample = sum(num_samples_per_step) // 2
        sampling_interval = 1 / samp_rate
        # compute the sample index we are "assigning" to each spectrum
        # and multiply by the sampling interval to get the equivalent physical time
        times = np.array([ midpoint_sample + (i * num_samples_per_sweep) for i in range(num_spectrums) ]) * sampling_interval

        # Compute the frequency array
        baseband_frequencies = np.fft.fftshift(np.fft.fftfreq(window_size, sampling_interval))
        frequencies = np.empty((window_size * num_steps))
        for i in range(num_steps):
            lower_bound = i * window_size
            upper_bound = (i + 1) * window_size
            frequencies[lower_bound:upper_bound] = baseband_frequencies + (samp_rate / 2) + (samp_rate * i)

        # Return the spectrogram.
        return Spectrogram(analytical_dynamic_spectra,
                           times,
                           frequencies,
                           'analytically-derived-spectrogram',
                           spectrum_type="amplitude")
    

def get_analytical_spectrogram(num_spectrums: int,
                               capture_config: CaptureConfig) -> Spectrogram:
    
    factory = _AnalyticalFactory()
    return factory.get_spectrogram(num_spectrums,
                                   capture_config)


def validate_analytically(spectrogram: Spectrogram,
                          capture_config: CaptureConfig,
                          absolute_tolerance: float) -> TestResults:

    analytical_spectrogram = get_analytical_spectrogram(spectrogram.num_times,
                                                        capture_config)


    test_results = TestResults()

    if is_close(analytical_spectrogram.times,
                spectrogram.times,
                absolute_tolerance):
        test_results.times_validated = True


    if is_close(analytical_spectrogram.frequencies,
                spectrogram.frequencies,
                absolute_tolerance):
        test_results.frequencies_validated = True

    test_results.spectrum_validated = {}
    for i in range(spectrogram.num_times):
        time = spectrogram.times[i]
        analytical_spectrum = analytical_spectrogram.dynamic_spectra[:, i]
        spectrum = spectrogram.dynamic_spectra[:, i]
        test_results.spectrum_validated[time] = is_close(analytical_spectrum, 
                                                         spectrum,
                                                         absolute_tolerance)

    return test_results