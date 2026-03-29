# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses
import typing
import abc

import pydantic
import numpy as np
import numpy.typing as npt

import spectre_server.core.events
import spectre_server.core.flowgraphs
import spectre_server.core.models
import spectre_server.core.batches
import spectre_server.core.spectrograms

from ._register import register_receiver
from ._base import Base, ReceiverComponents
from ._names import ReceiverName


def _is_close(
    ar: npt.NDArray[np.float32],
    ar_comparison: npt.NDArray[np.float32],
    absolute_tolerance: float,
) -> bool:
    """
    Checks if all elements in two arrays are element-wise close within a given tolerance.

    :param ar: First array for comparison.
    :param ar_comparison: Second array for comparison.
    :param absolute_tolerance: Absolute tolerance for element-wise comparison.
    :return: `True` if all elements are close within the specified tolerance, otherwise `False`.
    """
    return bool(np.all(np.isclose(ar, ar_comparison, atol=absolute_tolerance)))


M = typing.TypeVar("M", bound=pydantic.BaseModel)


class Solver(typing.Generic[M]):
    @abc.abstractmethod
    def solve(
        self, num_spectrums: int, model: M
    ) -> spectre_server.core.spectrograms.Spectrogram:
        """Subclasses should produce an analytically derived spectrogram for the `SignalGenerator` receiver
        according to the mode and input model.

        :param num_spectrums: The number of spectrums in the resulting spectrogram.
        :param model: The model containing the configurable parameters.
        """


class Solvers(ReceiverComponents[Solver]):
    """For each mode, produce an analytically-derived spectrogram."""


class CosineWaveSolver(
    Solver[spectre_server.core.models.SignalGeneratorCosineWaveModel]
):
    def solve(
        self,
        num_spectrums: int,
        model: spectre_server.core.models.SignalGeneratorCosineWaveModel,
    ) -> spectre_server.core.spectrograms.Spectrogram:
        """Produces the analytically-derived spectrogram for the `SignalGenerator` receiver operating in the mode `cosine_wave`."""

        # Calculate derived parameters a (sampling rate ratio) and p (sampled periods).
        a = int(model.sample_rate / model.frequency)
        p = int(model.window_size / a)

        # Create the analytical spectrum, which is constant in time.
        spectrum = np.zeros(model.window_size)
        spectral_amplitude = model.amplitude * model.window_size / 2
        spectrum[p] = spectral_amplitude
        spectrum[model.window_size - p] = spectral_amplitude

        # Align spectrum to naturally ordered frequency array.
        spectrum = np.fft.fftshift(spectrum)

        # Populate the spectrogram with identical spectra.
        dynamic_spectra = (
            np.ones((model.window_size, num_spectrums)) * spectrum[:, np.newaxis]
        )

        # Compute time array.
        sampling_interval = np.float32(1 / model.sample_rate)
        times = np.arange(num_spectrums) * model.window_hop * sampling_interval

        # Compute the frequency array.
        frequencies = (
            np.fft.fftshift(np.fft.fftfreq(model.window_size, sampling_interval))
            + model.center_frequency
        )

        return spectre_server.core.spectrograms.Spectrogram(
            dynamic_spectra,
            times,
            frequencies,
            spectre_server.core.spectrograms.SpectrumUnit.AMPLITUDE,
        )


class ConstantStaircaseSolver(
    Solver[spectre_server.core.models.SignalGeneratorConstantStaircaseModel]
):
    def solve(
        self,
        num_spectrums: int,
        model: spectre_server.core.models.SignalGeneratorConstantStaircaseModel,
    ) -> spectre_server.core.spectrograms.Spectrogram:
        """Produces the analytically-derived spectrogram for the `SignalGenerator` receiver operating in the mode `constant_staircase`."""

        # Calculate step sizes and derived parameters.
        num_samples_per_step = np.arange(
            model.min_samples_per_step,
            model.max_samples_per_step + 1,
            model.step_increment,
        )
        num_steps = len(num_samples_per_step)

        # Create the analytical spectrum, constant in time.
        spectrum = np.zeros(model.window_size * num_steps)
        step_count = 0
        for i in range(num_steps):
            step_count += 1
            spectral_amplitude = model.window_size * step_count
            spectrum[int(model.window_size / 2) + i * model.window_size] = (
                spectral_amplitude
            )

        # Populate the spectrogram with identical spectra.
        dynamic_spectra = (
            np.ones((model.window_size * num_steps, num_spectrums))
            * spectrum[:, np.newaxis]
        )

        # Compute time array
        num_samples_per_sweep = sum(num_samples_per_step)
        sampling_interval = np.float32(1 / model.sample_rate)
        # compute the sample index we are "assigning" to each spectrum
        # and multiply by the sampling interval to get the equivalent physical time
        times = (
            np.array([(i * num_samples_per_sweep) for i in range(num_spectrums)])
            * sampling_interval
        )

        # Compute the frequency array
        baseband_frequencies = np.fft.fftshift(
            np.fft.fftfreq(model.window_size, sampling_interval)
        )
        frequencies = np.empty((model.window_size * num_steps), dtype=np.float32)
        for i in range(num_steps):
            lower_bound = i * model.window_size
            upper_bound = (i + 1) * model.window_size
            frequencies[lower_bound:upper_bound] = (
                baseband_frequencies + (model.sample_rate / 2) + (model.sample_rate * i)
            )

        # Return the spectrogram.
        return spectre_server.core.spectrograms.Spectrogram(
            dynamic_spectra,
            times,
            frequencies,
            spectre_server.core.spectrograms.SpectrumUnit.AMPLITUDE,
        )


@dataclasses.dataclass(frozen=True)
class _Mode:
    COSINE_WAVE = "cosine_wave"
    CONSTANT_STAIRCASE = "constant_staircase"


@register_receiver(ReceiverName.SIGNAL_GENERATOR)
class SignalGenerator(Base):
    def __init__(
        self, *args, solvers: typing.Optional[Solvers] = None, **kwargs
    ) -> None:
        """An entirely software-defined receiver, which generates synthetic signals."""
        super().__init__(*args, **kwargs)

        self.__solvers = solvers or Solvers()

        self.add_mode(
            _Mode.COSINE_WAVE,
            spectre_server.core.models.SignalGeneratorCosineWaveModel,
            spectre_server.core.flowgraphs.SignalGeneratorCosineWave,
            spectre_server.core.events.FixedCenterFrequency,
            spectre_server.core.batches.IQStreamBatch,
        )
        self.add_solver(_Mode.COSINE_WAVE, CosineWaveSolver())

        self.add_mode(
            _Mode.CONSTANT_STAIRCASE,
            spectre_server.core.models.SignalGeneratorConstantStaircaseModel,
            spectre_server.core.flowgraphs.SignalGeneratorConstantStaircase,
            spectre_server.core.events.SweptCenterFrequency,
            spectre_server.core.batches.IQStreamBatch,
        )
        self.add_solver(_Mode.CONSTANT_STAIRCASE, ConstantStaircaseSolver())

    @property
    def solver(
        self,
    ) -> Solver:
        return self.__solvers.get(self.active_mode)

    def add_solver(self, mode: str, solver: Solver) -> None:
        self.__solvers.add(mode, solver)

    def validate_analytically(
        self,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
        model: pydantic.BaseModel,
        absolute_tolerance: float,
    ) -> dict[str, typing.Any]:
        """Validate a spectrogram generated during sessions with a `SignalGenerator` receiver operating
        in a particular mode.

        :param spectrogram: The spectrogram to be validated.
        :param absolute_tolerance: Tolerance level for numerical comparisons.
        :return: A dictionary summarising the validation outcome.
        """
        analytical_spectrogram = self.solver.solve(spectrogram.num_times, model)

        # Validate times and frequencies.
        times_validated = _is_close(
            analytical_spectrogram.times, spectrogram.times, absolute_tolerance
        )
        frequencies_validated = _is_close(
            analytical_spectrogram.frequencies,
            spectrogram.frequencies,
            absolute_tolerance,
        )

        # Validate each spectrum.
        spectrum_validated = {
            spectrogram.times[i]: _is_close(
                analytical_spectrogram.dynamic_spectra[:, i],
                spectrogram.dynamic_spectra[:, i],
                absolute_tolerance,
            )
            for i in range(spectrogram.num_times)
        }

        # Summarise results
        num_validated_spectrums = sum(spectrum_validated.values())
        num_invalid_spectrums = len(spectrum_validated) - num_validated_spectrums

        return {
            "times_validated": times_validated,
            "frequencies_validated": frequencies_validated,
            "spectrum_validated": spectrum_validated,
            "num_validated_spectrums": num_validated_spectrums,
            "num_invalid_spectrums": num_invalid_spectrums,
        }
