# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import typing
import datetime

import numpy as np
import numpy.typing as npt
import pyfftw

import spectre_server.core.batches
import spectre_server.core.exceptions
import spectre_server.core.spectrograms
import spectre_server.core.fields

from ._base import Base, BaseModel
from ._stfft import (
    get_buffer,
    get_window,
    get_fftw_obj,
    get_frequencies,
    get_num_spectrums,
    stfft,
)

_LOGGER = logging.getLogger(__name__)


def _stitch_steps(
    stepped_dynamic_spectra: npt.NDArray[np.float32], num_full_sweeps: int
) -> npt.NDArray[np.float32]:
    """For each full sweep, create a single spectrum by stitching together the spectrum at each step."""
    return stepped_dynamic_spectra.reshape((num_full_sweeps, -1)).T


def _average_over_steps(
    stepped_dynamic_spectra: npt.NDArray[np.float32],
) -> npt.NDArray[np.float32]:
    """Average the spectrums in each step totally in time."""
    return np.nanmean(stepped_dynamic_spectra[..., 1:], axis=-1)


def _compute_num_max_frames_in_step(
    num_samples: npt.NDArray[np.int32], window_size: int, window_hop: int
) -> int:
    """Compute the maximum number of frames for all steps, and all sweeps, in the batch."""
    return get_num_spectrums(int(np.max(num_samples)), window_size, window_hop)


def _compute_num_full_sweeps(center_frequencies: npt.NDArray[np.float32]) -> int:
    """Compute the total number of full sweeps in the batch.

    Since the number of each samples in each step is variable, we only know a sweep is complete
    when there is a sweep after it. So we can define the total number of *full* sweeps as the number of
    (freq_max, freq_min) pairs in center_frequencies. It is only at an instance of (freq_max, freq_min) pair
    in center frequencies that the frequency decreases, so, we can compute the number of full sweeps by
    counting the numbers of negative values in np.diff(center_frequencies).
    """
    return len(np.where(np.diff(center_frequencies) < 0)[0])


def _compute_num_steps_per_sweep(center_frequencies: npt.NDArray[np.float32]) -> int:
    """Compute the (ensured constant) number of steps in each sweep."""
    # Find the (step) indices corresponding to the minimum frequencies.
    min_freq_indices = np.where(center_frequencies == np.min(center_frequencies))[0]
    # Then, we evaluate the number of steps that has occured between them via np.diff over the indices.
    unique_num_steps_per_sweep = np.unique(np.diff(min_freq_indices))
    # We expect that the difference is always the same, so that the result of np.unique has a single element.
    if len(unique_num_steps_per_sweep) != 1:
        raise spectre_server.core.exceptions.InvalidSweepMetadataError(
            (
                "Irregular step count per sweep, "
                "expected a consistent number of steps per sweep"
            )
        )
    return int(unique_num_steps_per_sweep[0])


def _validate_center_frequencies_ordering(
    center_frequencies: npt.NDArray[np.float32], freq_step: float
) -> None:
    """Check that the center frequencies are well-ordered in the detached header."""
    min_frequency = np.min(center_frequencies)
    # Extract the expected difference between each step within a sweep.
    for i, diff in enumerate(np.diff(center_frequencies)):
        # The steps should either increase by freq_step or drop to the minimum.
        if (diff != freq_step) and (center_frequencies[i + 1] != min_frequency):
            raise spectre_server.core.exceptions.InvalidSweepMetadataError(
                f"Unordered center frequencies detected, I/Q samples have been mixed up"
            )


def _compute_stepped_dynamic_spectra(
    stepped_dynamic_spectra: npt.NDArray[np.float32],
    fftw_obj: pyfftw.FFTW,
    buffer: npt.NDArray[np.complex64],
    iq_data: npt.NDArray[np.complex64],
    window: npt.NDArray[np.float32],
    window_hop: int,
    num_full_sweeps: int,
    num_steps_per_sweep: int,
    num_samples: npt.NDArray[np.int32],
) -> None:
    """For each full sweep, compute execute a short-time discrete Fourier transform on the IQ samples for each step."""
    # Store the step index over all sweeps (doesn't reset each sweep).
    global_step_index = 0
    # Store the index of the first sample in the step.
    start_sample_index = 0

    for sweep_index in range(num_full_sweeps):
        for step_index in range(num_steps_per_sweep):

            # Extract how many samples are in the current step from the metadata.
            end_sample_index = start_sample_index + num_samples[global_step_index]

            # Compute the number of frames we can squeeze into the current step.
            num_frames = get_num_spectrums(
                num_samples[global_step_index], window.size, window_hop
            )

            # Execute a short time discrete fourier transform on the step, then shift the
            # zero-frequency component to the middle of the spectrum.
            stepped_dynamic_spectra[sweep_index, step_index, :, :num_frames] = (
                np.fft.fftshift(
                    stfft(
                        fftw_obj,
                        buffer,
                        iq_data[start_sample_index:end_sample_index],
                        window,
                        window_hop,
                    ),
                    axes=0,
                )
            )

            # Reassign the start_sample_index for the next step.
            start_sample_index = end_sample_index

            # Finally, increment the global step index
            global_step_index += 1


def _compute_frequencies(
    frequencies: npt.NDArray[np.float32],
    center_frequencies: npt.NDArray[np.float32],
    window_size: int,
    sample_rate: float,
) -> None:
    """Assign physical frequencies to each of the spectral components in the stitched spectrum."""
    baseband_frequencies = np.fft.fftshift(get_frequencies(window_size, sample_rate))

    for i, center_frequency in enumerate(np.unique(center_frequencies)):
        lower_bound = i * window_size
        upper_bound = (i + 1) * window_size
        frequencies[lower_bound:upper_bound] = baseband_frequencies + center_frequency


def _compute_times(
    times: npt.NDArray[np.float32],
    num_samples: npt.NDArray[np.int32],
    sample_rate: float,
    num_full_sweeps: int,
    num_steps_per_sweep: int,
) -> None:
    """Assign physical times to each swept spectrum. We use (by convention) the time of the first sample in each sweep"""
    sampling_interval = 1 / sample_rate
    cumulative_samples = 0
    for sweep_index in range(num_full_sweeps):
        # Assign a physical time to the spectrum for this sweep
        times[sweep_index] = cumulative_samples * sampling_interval

        # Find the total number of samples across the sweep.
        start_step = sweep_index * num_steps_per_sweep
        end_step = (sweep_index + 1) * num_steps_per_sweep

        # Update cumulative samples
        cumulative_samples += np.sum(num_samples[start_step:end_step])


def _swept_stfft(
    fftw_obj: pyfftw.FFTW,
    buffer: npt.NDArray[np.complex64],
    iq_data: npt.NDArray[np.complex64],
    window: npt.NDArray[np.float32],
    window_hop: int,
    sample_rate: float,
    frequency_hop: float,
    center_frequencies: npt.NDArray[np.float32],
    num_samples: npt.NDArray[np.int32],
) -> tuple[npt.NDArray[np.float32], npt.NDArray[np.float32], npt.NDArray[np.float32]]:
    _validate_center_frequencies_ordering(center_frequencies, frequency_hop)

    num_steps_per_sweep = _compute_num_steps_per_sweep(center_frequencies)
    num_full_sweeps = _compute_num_full_sweeps(center_frequencies)
    num_max_frames_in_step = _compute_num_max_frames_in_step(
        num_samples, window.size, window_hop
    )

    stepped_dynamic_spectra_shape = (
        num_full_sweeps,
        num_steps_per_sweep,
        window.size,
        num_max_frames_in_step,
    )

    # Pad with nan values up to the max number of frames to make computations simpler.
    stepped_dynamic_spectra = np.full(
        stepped_dynamic_spectra_shape, np.nan, dtype=np.float32
    )
    _compute_stepped_dynamic_spectra(
        stepped_dynamic_spectra,
        fftw_obj,
        buffer,
        iq_data,
        window,
        window_hop,
        num_full_sweeps,
        num_steps_per_sweep,
        num_samples,
    )

    # Assign physical frequencies to each spectral component in the spectrum for each sweep.
    frequencies = np.empty(num_steps_per_sweep * window.size, dtype=np.float32)
    _compute_frequencies(frequencies, center_frequencies, window.size, sample_rate)

    # Assign physical times to each spectrum in the spectrogram.
    times = np.empty(num_full_sweeps, dtype=np.float32)
    _compute_times(
        times, num_samples, sample_rate, num_full_sweeps, num_steps_per_sweep
    )

    dynamic_spectra = _stitch_steps(
        _average_over_steps(stepped_dynamic_spectra), num_full_sweeps
    )

    return times, frequencies, dynamic_spectra


def _prepend_num_samples(
    carryover_num_samples: npt.NDArray[np.int32],
    num_samples: npt.NDArray[np.int32],
    final_step_spans_two_batches: bool,
) -> npt.NDArray[np.int32]:
    """Prepend the number of samples from the final sweep of the previous batch, to the first
    sweep of the current batch."""
    if final_step_spans_two_batches:
        # In the case that the step has bled across batches, adjust the number of samples accordingly.
        num_samples[0] += carryover_num_samples[-1]
        return np.concatenate((carryover_num_samples[:-1], num_samples))
    else:
        return np.concatenate((carryover_num_samples, num_samples))


def _prepend_center_frequencies(
    carryover_center_frequencies: npt.NDArray[np.float32],
    center_frequencies: npt.NDArray[np.float32],
    final_step_spans_two_batches: bool,
) -> npt.NDArray[np.float32]:
    """Prepend the center frequencies from the final sweep of the previous batch, to the first
    sweep of the current batch."""
    if final_step_spans_two_batches:
        # In the case that final step has bled across batches, do not permit identical neighbours in the center frequency array.
        return np.concatenate((carryover_center_frequencies[:-1], center_frequencies))
    else:
        return np.concatenate((carryover_center_frequencies, center_frequencies))


def _prepend_iq_data(
    carryover_iq_data: npt.NDArray[np.complex64], iq_data: npt.NDArray[np.complex64]
) -> npt.NDArray[np.complex64]:
    """Prepend the IQ samples from the final sweep of the previous batch, to the first sweep
    of the current batch."""
    return np.concatenate((carryover_iq_data, iq_data))


def _get_final_sweep(
    previous_iq_data: npt.NDArray[np.complex64],
    previous_iq_metadata: spectre_server.core.batches.IQMetadata,
) -> tuple[npt.NDArray[np.complex64], npt.NDArray[np.float32], npt.NDArray[np.int32]]:
    """Get IQ samples and metadata from the final sweep of the previous batch."""

    if (
        previous_iq_metadata.center_frequencies is None
        or previous_iq_metadata.num_samples is None
    ):
        raise ValueError(f"Expected non-empty IQ metadata.")

    # Find the step index from the last sweep
    # [0] since the return of np.where is a 1 element Tuple,
    # containing a list of step indices corresponding to the smallest center frequencies
    # [-1] since we want the final step index, where the center frequency is minimised
    final_sweep_start_step_index = np.where(
        previous_iq_metadata.center_frequencies
        == np.min(previous_iq_metadata.center_frequencies)
    )[0][-1]

    # Isolate the data from the final sweep.
    final_center_frequencies = previous_iq_metadata.center_frequencies[
        final_sweep_start_step_index:
    ]
    final_num_samples = previous_iq_metadata.num_samples[final_sweep_start_step_index:]
    final_iq_data = previous_iq_data[-np.sum(final_num_samples) :]

    # Do a sanity check on the number of samples in the final sweep
    if len(final_iq_data) != np.sum(final_num_samples):
        raise ValueError(
            (
                f"Unexpected error! Mismatch in sample count for the final sweep data."
                f"Expected {np.sum(final_num_samples)} based on sweep metadata, but found "
                f" {len(final_iq_data)} IQ samples in the final sweep"
            )
        )

    return final_iq_data, final_center_frequencies, final_num_samples


def _reconstruct_initial_sweep(
    previous_iq_data: npt.NDArray[np.complex64],
    previous_iq_metadata: spectre_server.core.batches.IQMetadata,
    iq_data: npt.NDArray[np.complex64],
    iq_metadata: spectre_server.core.batches.IQMetadata,
) -> tuple[
    npt.NDArray[np.complex64], npt.NDArray[np.float32], npt.NDArray[np.int32], int
]:
    """Reconstruct the initial sweep of the current batch, using data from the previous batch.

    Specifically, we extract the data from the final sweep of the previous batch and prepend
    it to the first sweep of the current batch. Additionally, we return how many IQ samples
    we prepended, which will allow us to correct the spectrogram start time of the current batch.
    """

    # Extract the final sweep of the previous batch, to carryover to the first sweep of the current batch.
    carryover_iq_data, carryover_center_frequencies, carryover_num_samples = (
        _get_final_sweep(previous_iq_data, previous_iq_metadata)
    )

    # Prepend the iq data from the final sweep of the previous batch.
    iq_data = _prepend_iq_data(carryover_iq_data, iq_data)

    # Assess whether the final step in the previous batch, bleeds to the next.
    final_step_spans_two_batches = (
        carryover_center_frequencies[-1] == iq_metadata.center_frequencies[0]
    )

    # Prepend the iq metadata from the final sweep of the previous batch.
    center_frequencies = _prepend_center_frequencies(
        carryover_center_frequencies,
        iq_metadata.center_frequencies,
        final_step_spans_two_batches,
    )
    num_samples = _prepend_num_samples(
        carryover_num_samples, iq_metadata.num_samples, final_step_spans_two_batches
    )

    # Keep track of how many samples we prepended, so we can adjust the timing later.
    num_samples_prepended = int(np.sum(carryover_num_samples))

    return (iq_data, center_frequencies, num_samples, num_samples_prepended)


class SweptCenterFrequencyModel(BaseModel):
    window_size: spectre_server.core.fields.Field.window_size = 1024
    window_hop: spectre_server.core.fields.Field.window_hop = 1024
    window_type: spectre_server.core.fields.Field.window_type = (
        spectre_server.core.fields.WindowType.BLACKMAN
    )
    sample_rate: spectre_server.core.fields.Field.sample_rate = 32e3
    frequency_resolution: spectre_server.core.fields.Field.frequency_resolution = 0
    time_resolution: spectre_server.core.fields.Field.time_resolution = 0
    keep_signal: spectre_server.core.fields.Field.keep_signal = True
    frequency_hop: spectre_server.core.fields.Field.frequency_hop = 32e3
    output_type: spectre_server.core.fields.Field.output_type = (
        spectre_server.core.fields.OutputType.FC32
    )


class SweptCenterFrequency(
    Base[SweptCenterFrequencyModel, spectre_server.core.batches.IQStreamBatch]
):
    def __init__(
        self,
        tag: str,
        model: SweptCenterFrequencyModel,
        batch_cls: typing.Type[spectre_server.core.batches.IQStreamBatch],
    ) -> None:
        super().__init__(tag, model, batch_cls)
        self.__model = model
        self.__window = get_window(self.__model.window_type, self.__model.window_size)

        # Pre-allocate the buffer.
        self.__buffer = get_buffer(self.__model.window_size)

        # Defer the expensive FFTW plan creation until the first batch is being processed.
        # With this approach, we avoid a bug where filesystem events are missed because
        # the watchdog observer isn't set up in time before the receiver starts capturing data.
        self.__fftw_obj = None

        self.__output_type = self.__model.output_type

        # Initialise a cache to hold the previous batches data.
        self.__previous_batch: typing.Optional[
            spectre_server.core.batches.IQStreamBatch
        ] = None

    @property
    def _watch_extension(self) -> str:
        return self.__output_type

    def process(
        self, batch: spectre_server.core.batches.IQStreamBatch
    ) -> spectre_server.core.spectrograms.Spectrogram:
        """Compute a spectrogram of IQ samples captured at a center frequency periodically swept in
        fixed increments. Neighbouring IQ samples captured at the same frequency constitute a "step". Neighbouring
        steps captured at incrementally increasing center frequencies form a "sweep." A new sweep begins when the
        center frequency resets to its minimum value.

        A short-time discrete Fourier transform is computed for each step, with the resulting spectra averaged over
        in time to produce a single spectrum per step. The spectra for each step are stitched in frequency to form a single
        spectrum for each sweep. These swept spectra are stiched in time to produce the final spectrogram, which is saved to file
        in the FITS format.
        """
        _LOGGER.info(f"Reading the I/Q samples")
        iq_data = batch.cached_read_iq(self.__output_type)

        _LOGGER.info(f"Reading the tag metadata")
        iq_metadata = batch.hdr_file.cached_read()

        start_datetime = batch.start_datetime

        center_frequencies, num_samples = (
            iq_metadata.center_frequencies,
            iq_metadata.num_samples,
        )

        # If a previous batch is stored, the initial sweep may span two adjacent batched files.
        if self.__previous_batch is not None:
            # If this is the case, first reconstruct the initial sweep of the current batch
            # by prepending the final sweep of the previous batch.
            iq_data, center_frequencies, num_samples, num_samples_prepended = (
                _reconstruct_initial_sweep(
                    self.__previous_batch.cached_read_iq(self.__output_type),
                    self.__previous_batch.hdr_file.cached_read(),
                    iq_data,
                    iq_metadata,
                )
            )

            # Since we have prepended extra samples, we need to correct the spectrogram start time appropriately.
            elapsed_time = num_samples_prepended * (1 / self.__model.sample_rate)
            start_datetime -= datetime.timedelta(seconds=float(elapsed_time))

        if self.__fftw_obj is None:
            _LOGGER.info(f"Creating the FFTW plan")
            self.__fftw_obj = get_fftw_obj(self.__buffer)

        _LOGGER.info("Executing the short-time FFT")
        # Compute the short-time discrete fourier transform.
        times, frequencies, dynamic_spectra = _swept_stfft(
            self.__fftw_obj,
            self.__buffer,
            iq_data,
            self.__window,
            self.__model.window_hop,
            self.__model.sample_rate,
            self.__model.frequency_hop,
            center_frequencies,
            num_samples,
        )

        _LOGGER.info("Creating the spectrogram")
        spectrogram = spectre_server.core.spectrograms.Spectrogram(
            dynamic_spectra,
            times,
            frequencies,
            spectre_server.core.spectrograms.SpectrumUnit.AMPLITUDE,
            start_datetime,
        )

        spectrogram = spectre_server.core.spectrograms.time_average(
            spectrogram, resolution=self.__model.time_resolution
        )
        spectrogram = spectre_server.core.spectrograms.frequency_average(
            spectrogram, resolution=self.__model.frequency_resolution
        )

        # If the previous batch exists, then by this point it has already been processed.
        if self.__previous_batch is not None:
            if not self.__model.keep_signal:
                _LOGGER.info(f"Deleting the I/Q samples from the previous batch")
                self.__previous_batch.delete_iq(self.__output_type)

                _LOGGER.info(f"Deleting metadata from the previous batch")
                self.__previous_batch.hdr_file.delete()

        # Assign the current batch to be used as the previous batch at the next call of this method.
        self.__previous_batch = batch

        return spectrogram
