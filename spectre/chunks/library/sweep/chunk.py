# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Tuple
from typing import Optional
from datetime import timedelta
from dataclasses import dataclass

import numpy as np

from spectre.chunks.chunk_register import register_chunk
from spectre.spectrograms.spectrogram import Spectrogram
from spectre.chunks.library.fixed.chunk import BinChunk, FitsChunk
from spectre.cfg import DEFAULT_DATETIME_FORMAT
from spectre.chunks.base import SPECTREChunk, ChunkFile
from spectre.exceptions import InvalidSweepMetadataError


@dataclass
class SweepMetadata:
    """Wrapper for metadata required to assign center frequencies to each IQ sample in the chunk.
    
    center_frequencies is an ordered list containing all the center frequencies that the IQ samples
    were collected at. Typically, these will be ordered in "steps", where each step corresponds to
    IQ samples collected at a constant center frequency:

    (freq_0, freq_1, ..., freq_M, freq_0, freq_1, ..., freq_M, ...), freq_0 < freq_1 < ... < freq_M

    The n'th element of the num_samples list, tells us how many samples were collected at the n'th
    element of center_frequencies:

    Number of samples: (num_samples_at_freq_0, num_samples_at_freq_1, ...)

    Both these lists together allow us to map for each IQ sample, the center frequency it was collected at.
    """
    center_frequencies: np.ndarray
    num_samples: np.ndarray


@register_chunk('sweep')
class Chunk(SPECTREChunk):
    def __init__(self, chunk_start_time, tag):
        super().__init__(chunk_start_time, tag)

        self.add_file(BinChunk(self.chunk_parent_path, self.chunk_name))
        self.add_file(FitsChunk(self.chunk_parent_path, self.chunk_name))
        self.add_file(HdrChunk(self.chunk_parent_path, self.chunk_name))


    def build_spectrogram(self, 
                          previous_chunk: Optional[SPECTREChunk] = None) -> Spectrogram:
        """Create a spectrogram by performing a Short Time FFT on the (swept) IQ samples for this chunk."""
        IQ_data = self.read_file("bin")
        millisecond_correction, sweep_metadata = self.read_file("hdr")

        if previous_chunk:
            IQ_data, sweep_metadata, num_samples_prepended = self.__reconstruct_initial_sweep(previous_chunk,
                                                                                              IQ_data,
                                                                                              sweep_metadata)
            
            chunk_start_time, millisecond_correction = self.__correct_timing(millisecond_correction,
                                                                             num_samples_prepended)
        else:
            chunk_start_time = self.chunk_start_time

        microsecond_correction = millisecond_correction * 1e3

        times, frequencies, dynamic_spectra = self.__do_STFFT(IQ_data, 
                                                              sweep_metadata)
        
        return Spectrogram(dynamic_spectra,
                           times,
                           frequencies,
                           self.tag,
                           chunk_start_time,
                           microsecond_correction,
                           spectrum_type = "amplitude")
    
    def __get_final_sweep(self,
                          previous_chunk: SPECTREChunk) -> Tuple[np.ndarray, SweepMetadata]:
        """Get data from the final sweep of the previous chunk."""
        # unpack the data from the previous chunk
        previous_IQ_data = previous_chunk.read_file("bin")
        _, previous_sweep_metadata = previous_chunk.read_file("hdr")
        # find the step index from the last sweep
        # [0] since the return of np.where is a 1 element Tuple, 
        # containing a list of step indices corresponding to the smallest center frequencies
        # [-1] since we want the final step index, where the center frequency is minimised
        final_sweep_start_step_index = np.where(previous_sweep_metadata.center_frequencies == np.min(previous_sweep_metadata.center_frequencies))[0][-1]
        # isolate the data from the final sweep
        final_center_frequencies = previous_sweep_metadata.center_frequencies[final_sweep_start_step_index:]
        final_num_samples = previous_sweep_metadata.num_samples[final_sweep_start_step_index:]
        final_sweep_IQ_data = previous_IQ_data[-np.sum(final_num_samples):]

        # sanity check on the number of samples in the final sweep
        if len(final_sweep_IQ_data) != np.sum(final_num_samples):
            raise ValueError((f"Unexpected error! Mismatch in sample count for the final sweep data."
                              f"Expected {np.sum(final_num_samples)} based on sweep metadata, but found "
                              f" {len(final_sweep_IQ_data)} IQ samples in the final sweep"))
        
        return final_sweep_IQ_data, SweepMetadata(final_center_frequencies, final_num_samples)


    def __prepend_IQ_data(self,
                          carryover_IQ_data: np.ndarray,
                          IQ_data: np.ndarray) -> np.ndarray:
        """Prepend the IQ samples from the final sweep of the previous chunk."""
        return np.concatenate((carryover_IQ_data, IQ_data))
    

    def __prepend_center_frequencies(self,
                                     carryover_center_frequencies: np.ndarray,
                                     center_frequencies: np.ndarray,
                                     final_sweep_spans_two_chunks: bool)-> np.ndarray:
        """Prepend the center frequencies from the final sweep of the previous chunk."""
        # in the case that the sweep has bled across chunks,
        # do not permit identical neighbours in the center frequency array
        if final_sweep_spans_two_chunks:
            # truncate the final frequency to prepend (as it already exists in the array we are appending to in this case)
            carryover_center_frequencies = carryover_center_frequencies[:-1]
        return np.concatenate((carryover_center_frequencies, center_frequencies))
    

    def __prepend_num_samples(self,
                              carryover_num_samples: np.ndarray,
                              num_samples: np.ndarray,
                              final_sweep_spans_two_chunks: bool) -> np.ndarray:
        """Prepend the number of samples from the final sweep of the previous chunk."""
        if final_sweep_spans_two_chunks:
            # ensure the number of samples from the final step in the previous chunk are accounted for
            num_samples[0] += carryover_num_samples[-1]
            # and truncate as required
            carryover_num_samples = carryover_num_samples[:-1]
        return np.concatenate((carryover_num_samples, num_samples))
    

    def __reconstruct_initial_sweep(self,
                                    previous_chunk: SPECTREChunk,
                                    IQ_data: np.ndarray,
                                    sweep_metadata: SweepMetadata) -> Tuple[np.ndarray, SweepMetadata, int]:
        """Reconstruct the initial sweep of the current chunk, using data from the previous chunk."""

        # carryover the final sweep of the previous chunk, and prepend that data to the current chunk data
        carryover_IQ_data, carryover_sweep_metadata = self.__get_final_sweep(previous_chunk)
        IQ_data = self.__prepend_IQ_data(carryover_IQ_data,
                                         IQ_data)
        
        # if the final sweep of the previous sweep has bled through to the current chunk
        final_sweep_spans_two_chunks = carryover_sweep_metadata.center_frequencies[-1] == sweep_metadata.center_frequencies[0]
        
        center_frequencies = self.__prepend_center_frequencies(carryover_sweep_metadata.center_frequencies,
                                                               sweep_metadata.center_frequencies,
                                                               final_sweep_spans_two_chunks)
        num_samples = self.__prepend_num_samples(carryover_sweep_metadata.num_samples,
                                                 sweep_metadata.num_samples,
                                                 final_sweep_spans_two_chunks)
        
        num_samples_prepended = np.sum(carryover_sweep_metadata.num_samples)
        
        return IQ_data, SweepMetadata(center_frequencies, num_samples), num_samples_prepended


    def __correct_timing(self,
                         millisecond_correction: int,
                         num_samples_prepended: int):
        """Correct the start time for this chunk based on the number of samples we prepended reconstructing the initial sweep."""
        elapsed_time = num_samples_prepended * (1 / self.capture_config.get("samp_rate"))

        corrected_datetime = self.chunk_start_datetime + timedelta(milliseconds = millisecond_correction) - timedelta(seconds = float(elapsed_time))
        return corrected_datetime.strftime(DEFAULT_DATETIME_FORMAT), corrected_datetime.microsecond * 1e-3


    def __validate_center_frequencies_ordering(self,
                                               center_frequencies) -> None:
        """Check that the center frequencies are well-ordered in the detached header."""
        min_frequency = np.min(center_frequencies)
        diffs = np.diff(center_frequencies)
        # Extract the expected difference between each step within a sweep. 
        freq_step = self.capture_config.get("freq_step")
        # Validate frequency steps
        for i, diff in enumerate(diffs):
            # steps should either increase by freq_step or drop to the minimum
            if (diff != freq_step) and (center_frequencies[i + 1] != min_frequency):
                raise InvalidSweepMetadataError(f"Unordered center frequencies detected")
    

    def __compute_num_steps_per_sweep(self,
                                      center_frequencies: np.ndarray) -> int:
        """Compute the (ensured constant) number of steps in each sweep."""
        # find the (step) indices corresponding to the minimum frequencies
        min_freq_indices = np.where(center_frequencies == np.min(center_frequencies))[0]
        # then, we evaluate the number of steps that has occured between them via np.diff over the indices
        unique_num_steps_per_sweep = np.unique(np.diff(min_freq_indices))
        # we expect that the difference is always the same, so that the result of np.unique has a single element
        if len(unique_num_steps_per_sweep) != 1:
            raise InvalidSweepMetadataError(("Irregular step count per sweep, "
                                             "expected a consistent number of steps per sweep"))
        return int(unique_num_steps_per_sweep[0])
    

    def __compute_num_full_sweeps(self,
                                  center_frequencies: np.ndarray) -> int:
        """Compute the total number of full sweeps over the chunk.

        Since the number of each samples in each step is variable, we only know a sweep is complete
        when there is a sweep after it. So we can define the total number of *full* sweeps as the number of 
        (freq_max, freq_min) pairs in center_frequencies. It is only at an instance of (freq_max, freq_min) pair 
        in center frequencies that the frequency decreases, so, we can compute the number of full sweeps by 
        counting the numbers of negative values in np.diff(center_frequencies)
        """
        return len(np.where(np.diff(center_frequencies) < 0)[0])


    def __compute_num_max_slices_in_step(self, num_samples: np.ndarray) -> int:
        """Compute the maximum number of slices over all steps, in all sweeps over the chunk."""
        return self.SFT.upper_border_begin(np.max(num_samples))[1]


    def __fill_stepped_dynamic_spectra(self,
                                       stepped_dynamic_spectra: np.ndarray,
                                       IQ_data: np.ndarray,
                                       num_samples: np.ndarray,
                                       num_full_sweeps: int,
                                       num_steps_per_sweep: int) -> None:
        """Compute the dynamic spectra for the input IQ samples for each step.
        
        All IQ samples per step were collected at the same center frequency.
        """
        # global_step_index will hold the step index over all sweeps (doesn't reset each sweep)
        # start_sample_index will hold the index of the first sample in the step
        global_step_index, start_sample_index = 0, 0
        for sweep_index in range(num_full_sweeps):
            for step_index in range(num_steps_per_sweep):
                # extract how many samples are in the current step from the metadata
                end_sample_index = start_sample_index + num_samples[global_step_index]
                # compute the number of slices in the current step based on the window we defined on the capture config
                num_slices = self.SFT.upper_border_begin(num_samples[global_step_index])[1]
                # perform a short time fast fourier transform on the step
                complex_spectra = self.SFT.stft(IQ_data[start_sample_index:end_sample_index], 
                                           p0=0, 
                                           p1=num_slices)
                # and pack the absolute values into the stepped spectrogram where the step slot is padded to the maximum size for ease of processing later)
                stepped_dynamic_spectra[sweep_index, step_index, :, :num_slices] = np.abs(complex_spectra)
                # reassign the start_sample_index for the next step
                start_sample_index = end_sample_index
                # and increment the global step index
                global_step_index += 1
        

    def __fill_frequencies(self,
                           frequencies: np.ndarray,
                           center_frequencies: np.ndarray,
                           base_band_frequencies: np.ndarray,
                           window_size: int) -> None:
        """Assign physical frequencies to each of the swept spectral components."""
        for i, center_frequency in enumerate(np.unique(center_frequencies)):
            lower_bound = i * window_size
            upper_bound = (i + 1) * window_size
            frequencies[lower_bound:upper_bound] = (base_band_frequencies + center_frequency)
    

    def __fill_times(self,
                     times: np.ndarray,
                     num_samples: np.ndarray,
                     num_full_sweeps: int,
                     num_steps_per_sweep: int) -> None:
        """Assign physical times to each swept spectrum. We use (by convention) the time of the midpoint sample in each sweep."""

        sampling_interval = 1 / self.capture_config.get("samp_rate")
        cumulative_samples = 0
        for sweep_index in range(num_full_sweeps):
            # find the total number of samples across the sweep
            start_step = sweep_index * num_steps_per_sweep
            end_step = (sweep_index + 1) * num_steps_per_sweep
            num_samples_in_sweep = np.sum(num_samples[start_step:end_step])
            
            # compute the midpoint sample in the sweep
            midpoint_sample = cumulative_samples + num_samples_in_sweep // 2

            # update cumulative samples
            cumulative_samples += num_samples_in_sweep

            # assign a physical time to the spectrum for this sweep
            times[sweep_index] = midpoint_sample * sampling_interval
    
    
    def __average_over_steps(self, 
                             stepped_dynamic_spectra: np.ndarray) -> None:
        """Average the spectrums in each step totally in time."""
        return np.nanmean(stepped_dynamic_spectra[..., 1:], axis=-1)
    

    def __stitch_steps(self,
                       stepped_dynamic_spectra: np.ndarray,
                       num_full_sweeps: int) -> np.ndarray:
        """For each full sweep, create a swept spectrum by stitching together the spectrum at each of the steps."""
        return stepped_dynamic_spectra.reshape((num_full_sweeps, -1)).T
    

    def __do_STFFT(self,
                   IQ_data: np.ndarray,
                   sweep_metadata: SweepMetadata):
        """Perform a Short Time FFT on the input swept IQ samples."""
        self.__validate_center_frequencies_ordering(sweep_metadata.center_frequencies)

        window_size = len(self.SFT.win)

        num_steps_per_sweep = self.__compute_num_steps_per_sweep(sweep_metadata.center_frequencies)
        num_full_sweeps = self.__compute_num_full_sweeps(sweep_metadata.center_frequencies)
        num_max_slices_in_step = self.__compute_num_max_slices_in_step(sweep_metadata.num_samples)
        
        stepped_dynamic_spectra_shape = (num_full_sweeps, 
                                         num_steps_per_sweep, 
                                         window_size, 
                                         num_max_slices_in_step)
        stepped_dynamic_spectra = np.full(stepped_dynamic_spectra_shape, np.nan)

        
        frequencies = np.empty(num_steps_per_sweep * window_size)
        times = np.empty(num_full_sweeps)

        self.__fill_stepped_dynamic_spectra(stepped_dynamic_spectra,
                                            IQ_data,
                                            sweep_metadata.num_samples,
                                            num_full_sweeps,
                                            num_steps_per_sweep)
        
        self.__fill_frequencies(frequencies,
                                sweep_metadata.center_frequencies,
                                self.SFT.f,
                                window_size)
        
        self.__fill_times(times,
                          sweep_metadata.num_samples,
                          num_full_sweeps,
                          num_steps_per_sweep)

        averaged_spectra = self.__average_over_steps(stepped_dynamic_spectra)
        dynamic_spectra = self.__stitch_steps(averaged_spectra,
                                              num_full_sweeps)

        return times, frequencies, dynamic_spectra
    

class HdrChunk(ChunkFile):
    def __init__(self, chunk_parent_path: str, chunk_name: str):
        super().__init__(chunk_parent_path, chunk_name, "hdr")

    def read(self) -> Tuple[int, SweepMetadata]:
        hdr_contents = self._read_file_contents()
        millisecond_correction = self._get_millisecond_correction(hdr_contents)
        center_frequencies = self._get_center_frequencies(hdr_contents)
        num_samples = self._get_num_samples(hdr_contents)
        self._validate_frequencies_and_samples(center_frequencies, 
                                               num_samples)
        
        return millisecond_correction, SweepMetadata(center_frequencies, num_samples)
        

    def _read_file_contents(self) -> np.ndarray:
        with open(self.file_path, "rb") as fh:
            return np.fromfile(fh, dtype=np.float32)


    def _get_millisecond_correction(self, hdr_contents: np.ndarray) -> int:
        ''' Millisecond correction is an integral quantity, but stored in the detached header as a 32-bit float.'''
        millisecond_correction_as_float = float(hdr_contents[0])

        if not millisecond_correction_as_float.is_integer():
            raise TypeError(f"Expected integer value for millisecond correction, but got {millisecond_correction_as_float}")
        
        return int(millisecond_correction_as_float)


    def _get_center_frequencies(self, hdr_contents: np.ndarray) -> np.ndarray:
        ''' 
        Detached header contents are stored in (center_freq_i, num_samples_at_center_freq_i) pairs
        Return only a list of center frequencies, by skipping over file contents in twos.
        '''
        return hdr_contents[1::2]


    def _get_num_samples(self, hdr_contents: np.ndarray) -> np.ndarray:
        ''' 
        Detached header contents are stored in (center_freq_i, num_samples_at_center_freq_i) pairs
        Return only the number of samples at each center frequency, by skipping over file contents in twos.
        Number of samples is an integral quantity, but stored in the detached header as a 32-bit float.
        Types are checked before return.
        '''
        num_samples_as_float = hdr_contents[2::2]
        if not all(num_samples_as_float == num_samples_as_float.astype(int)):
            raise InvalidSweepMetadataError("Number of samples per frequency is expected to describe an integer")
        return num_samples_as_float.astype(int)


    def _validate_frequencies_and_samples(self, center_frequencies: np.ndarray, num_samples: np.ndarray) -> None:
        """Validates that the center frequencies and the number of samples arrays have the same length."""
        if len(center_frequencies) != len(num_samples):
            raise InvalidSweepMetadataError("Center frequencies and number of samples arrays are not the same length")
