import numpy as np
from typing import Tuple, Optional
from scipy.signal import ShortTimeFFT, get_window
from datetime import datetime, timedelta

from cfg import (
    DEFAULT_TIME_FORMAT
)
from spectre.file_handlers.chunks.SPECTREChunk import SPECTREChunk
from spectre.file_handlers.chunks.chunk_register import register_chunk
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.file_handlers.chunks.library.sweep.HdrChunk import HdrChunk
from spectre.file_handlers.chunks.library.default.BinChunk import BinChunk
from spectre.file_handlers.chunks.library.default.FitsChunk import FitsChunk

@register_chunk('sweep')
class Chunk(SPECTREChunk):
    def __init__(self, chunk_start_time, tag):
        super().__init__(chunk_start_time, tag)

        self.add_file(BinChunk(self.chunk_parent_path, self.chunk_name))
        self.add_file(FitsChunk(self.chunk_parent_path, self.chunk_name))
        self.add_file(HdrChunk(self.chunk_parent_path, self.chunk_name))

        # intialise attributes which are used by build_spectrogram and its helper methods 
        self.window: Optional[np.ndarray] = None
        self.SFT: Optional[ShortTimeFFT] = None
        self.num_steps_per_sweep: Optional[int] = None
        self.num_full_sweeps: Optional[int] = None
        self.window_size: Optional[int] = None
        self.samp_rate: Optional[float] = None
        self.sweep_metadata: Optional[Tuple[np.ndarray, np.ndarray]] = None
        self.center_frequencies: Optional[np.ndarray] = None
        self.num_samples: Optional[np.ndarray] = None
        self.prep_sweep_metadata: Optional[Tuple[np.ndarray, np.ndarray]] =None
        self.prep_center_frequencies: Optional[np.ndarray] = None
        self.prep_num_samples: Optional[np.ndarray] = None
        self.sweep_IQ_data: Optional[np.ndarray] = None
        self.prep_sweep_IQ_data: Optional[np.ndarray] = None

    def build_spectrogram(self, previous_chunk: Optional[SPECTREChunk] = None) -> Spectrogram:
        # read the (raw) swept IQ data
        self.sweep_IQ_data = self.read_file("bin")
        # read the millisecond correction and sweep metadata
        millisecond_correction, self.sweep_metadata = self.read_file("hdr")

        # if the previous chunk is specified, it is indicating we need to reconstruct the initial sweep
        if previous_chunk:
            self._reconstruct_initial_sweep(previous_chunk)
            # since we have prepended the initial sweep, we need to correct the chunk start time and millisecond correction of the spectrogram
            # (since the prepended samples occured *before* in time the start of the current chunk instance)
            chunk_start_time, millisecond_correction = self._get_corrected_timing(millisecond_correction)
        else:
            # otherwise we can simply use the chunk start time for the current chunk
            chunk_start_time = self.chunk_start_time

        # set the sweep metadata attributes explictly 
        (self.center_frequencies, self.num_samples) = self.sweep_metadata
        # convert the millisecond correction to a microsecond correction
        microsecond_correction = millisecond_correction * 1000
        # and (essentially) perform the STFFT on the IQ samples
        time_seconds, freq_MHz, dynamic_spectra = self._do_STFFT()

        return Spectrogram(
            dynamic_spectra=np.array(dynamic_spectra, dtype='float64'),
            time_seconds=np.array(time_seconds, dtype='float64'),
            freq_MHz=np.array(freq_MHz, dtype='float64'),
            tag=self.tag,
            chunk_start_time=chunk_start_time,
            microsecond_correction=microsecond_correction,
            spectrum_type="amplitude"
        )


    def _reconstruct_initial_sweep(self, previous_chunk: SPECTREChunk):
        # extract the swept IQ samples, and sweep metadata for the final sweep of the previous chunk
        # and set as attributes
        self.prep_sweep_IQ_data, self.prep_sweep_metadata = self._get_final_sweep_previous_chunk(previous_chunk)
        # use these (now defined) attributes and prepend to the existing sweep data
        self._prepend_sweep_IQ_data()
        self._prepend_sweep_metadata()
        return


    def _get_final_sweep_previous_chunk(self, previous_chunk: SPECTREChunk) -> Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        # read the entirety of the raw IQ data from the previous chunk
        prev_sweep_IQ_data = previous_chunk.read_file("bin")
        # read the sweep metadata from the header of the previous chunk
        _, (prev_center_freqs, prev_num_samples) = previous_chunk.read_file("hdr")
        # extract the (step) index of the start step of the final sweep
        final_sweep_start_step_index = np.where(prev_center_freqs == np.min(prev_center_freqs))[0][-1]
        # use this to isolate the data corresponding to the final sweep
        final_center_freqs = prev_center_freqs[final_sweep_start_step_index:]
        final_num_samples = prev_num_samples[final_sweep_start_step_index:]
        final_sweep_IQ_data = prev_sweep_IQ_data[-np.sum(final_num_samples):]

        # sanity check on the number of samples in teh final sweep
        if len(final_sweep_IQ_data) != np.sum(final_num_samples):
            raise ValueError("Unexpected error! Mismatch in sample count for the final sweep data")

        # return the data for the final sweep as required
        return final_sweep_IQ_data, (final_center_freqs, final_num_samples)


    def _prepend_sweep_IQ_data(self) -> None:
        # simple concatenation for the IQ_data
        self.sweep_IQ_data = np.concatenate((self.prep_sweep_IQ_data, self.sweep_IQ_data))
        return 
    

    def _prepend_sweep_metadata(self) -> Tuple[np.ndarray, np.ndarray]:
        # first unpack the metadata
        prepend_center_frequencies, prepend_num_samples = self.prep_sweep_metadata
        center_frequencies, num_samples = self.sweep_metadata

        # if the step from the previous chunk has bled over to the current chunk
        # (in other words, if the frequency of the final step of the previous chunk is equal to the frequency of the first step in the current chunk)
        # then we need to be careful about how we prepend (to avoid duplicate adjacent frequencies in the center frequency array, describing the same step)
        if prepend_center_frequencies[-1] == center_frequencies[0]:
            # truncate the final frequency to prepend (as it already exists in the array we are appending to in this case)
            prepend_center_frequencies = prepend_center_frequencies[:-1]
            # ensure the number of samples from the step in the previous chunk are accounted for
            num_samples[0] += prepend_num_samples[-1]
            # and truncate as required
            prepend_num_samples = prepend_num_samples[:-1]

        # now perform a basic concatenation
        center_frequencies = np.concatenate((prepend_center_frequencies, center_frequencies))
        num_samples = np.concatenate((prepend_num_samples, num_samples))
        # and can set the attribute
        self.sweep_metadata = (center_frequencies, num_samples)
        return
    

    def _get_corrected_timing(self, millisecond_correction: int) -> Tuple[str, int]:
        # extract the number of samples per step that we preneded
        _, prepend_num_samples = self.prep_sweep_metadata
        # and compute the total number of samples that we prepended
        total_samples_to_prepend = np.sum(prepend_num_samples)
        # we can use this to infer the exact amount of time that elapsed during collection of the prepended samples
        sampling_interval = 1 / self.capture_config.get("samp_rate")
        elapsed_seconds = sampling_interval * total_samples_to_prepend
        # subtract this from the (millisecond corrected) chunk start time for the current chunk
        corrected_datetime = self.chunk_start_datetime + timedelta(milliseconds=millisecond_correction) - timedelta(seconds=elapsed_seconds)
        # return the chunk_start_time (i.e. formatted as a string, truncated to second precision), along with the millisecond correction in order to recover full accuracy
        return datetime.strftime(corrected_datetime, DEFAULT_TIME_FORMAT), corrected_datetime.microsecond / 1000


    def _do_STFFT(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        # set the attributes used to define the swept STFFT procedure
        self._initialize_STFFT_params()
        # create the stepped spectrogram
        stepped_dynamic_spectra = self._compute_stepped_dynamic_spectra()
        # average totally in time the slices for each spectrogram
        # so that now each step has been assigned a single spectrum
        averaged_stepped_spectra = self._average_over_steps(stepped_dynamic_spectra)
        # create the swept dynamic spectra by assuming that each step is time coincident
        # and stitching the spectrums for each step in a sweep into a single spectrum
        # thus assigning one (swept) spectrum to each sweep
        swept_dynamic_spectra = self._stitch_steps(averaged_stepped_spectra)
        # assign times to each of the swept spectrums
        time_seconds = self._compute_time_seconds()
        freq_MHz = self._compute_frequencies()
        return time_seconds, freq_MHz, swept_dynamic_spectra


    def _initialize_STFFT_params(self):
        window_type = self.capture_config.get("window_type")
        window_params = self.capture_config.get("window_kwargs").values()
        self.window_size = self.capture_config.get("window_size")
        self.window = get_window((window_type, 
                                  *window_params), 
                                  self.window_size)
        self.samp_rate = self.capture_config.get("samp_rate")
        self.SFT = ShortTimeFFT(self.window, fs=self.samp_rate, fft_mode="centered", **self.capture_config.get("STFFT_kwargs"))
        self.num_steps_per_sweep = self._compute_num_steps_per_sweep()
        self.num_full_sweeps = self._compute_num_full_sweeps()
        self.num_max_slices_in_step = self._compute_num_max_slices_in_step()


    def _compute_num_steps_per_sweep(self) -> int:
        # find the indices of the minimum steps in each sweep
        min_freq_indices = np.where(self.center_frequencies == np.min(self.center_frequencies))[0]
        # ensure that number of steps per sweep is unique, and return the value
        unique_num_steps_per_sweep = np.unique(np.diff(min_freq_indices))
        if len(unique_num_steps_per_sweep) != 1:
            raise ValueError("Irregular step count per sweep")
        return int(unique_num_steps_per_sweep[0])


    def _compute_num_full_sweeps(self) -> int:
        # Since the number of each samples in each step is variable, we only know a sweep is complete
        # when there is a sweep after it. So we can define the total number of *full* sweeps as the number of 
        # (freq_max, freq_min) pairs in center_frequencies. Since at the sweep boundaries this is the only time
        # that the frequency step decreases, we can compute the number of full sweeps by counting the numbers of negative
        # values in np.diff(center_frequencies)
        return len(np.where(np.diff(self.center_frequencies) < 0)[0])


    def _compute_num_max_slices_in_step(self) -> int:
        # use scipy's SFT to compute the max number of slices in all steps
        return self.SFT.upper_border_begin(np.max(self.num_samples))[1]


    def _compute_stepped_dynamic_spectra(self) -> np.ndarray:
        # prime an array to hold the stepped dynamic spectra
        stepped_dynamic_spectra_shape = (self.num_full_sweeps, self.num_steps_per_sweep, self.window_size, self.num_max_slices_in_step)
        stepped_dynamic_spectra = np.full(stepped_dynamic_spectra_shape, np.nan)

        # global_step_index will hold the step index over all sweeps (doesn't reset each sweep)
        # start_sample_index will hold the index of the first sample in the step
        global_step_index, start_sample_index = 0, 0
        for sweep_index in range(self.num_full_sweeps):
            for step_index in range(self.num_steps_per_sweep):
                # extract how many samples are in the current step from the metadata
                end_sample_index = start_sample_index + self.num_samples[global_step_index]
                # compute the number of slices in the current step based on the window we defined on the capture config
                num_slices = self.SFT.upper_border_begin(self.num_samples[global_step_index])[1]
                # perform a short time fast fourier transform on the step
                complex_spectra = self.SFT.stft(self.sweep_IQ_data[start_sample_index:end_sample_index], p0=0, p1=num_slices)
                # and pack the absolute values into the stepped spectrogram where the step slot is padded to the maximum size for ease of processing later)
                stepped_dynamic_spectra[sweep_index, step_index, :, :num_slices] = np.abs(complex_spectra)
                # reassign the start_sample_index for the next step
                start_sample_index = end_sample_index
                # and increment the global step index
                global_step_index += 1
        return stepped_dynamic_spectra

    def _average_over_steps(self, stepped_spectra: np.ndarray) -> np.ndarray:
        # average the spectrums in each step totally in time to assign one spectrum per step
        return np.nanmean(stepped_spectra[..., 1:], axis=-1)

    def _compute_time_seconds(self) -> np.ndarray:
        # initialise an (ordered) array to hold the sample indices we will assign to each swept spectrum
        assigned_sample_indices = []
        # initialise a variable which will hold the cumulative samples in all previous sweeps
        # since naturally we haven't started yet at this point in the code, it's now zero!
        cumulative_samples = 0
        # iterate through each sweep
        for sweep_index in range(self.num_full_sweeps):
            # find the step index for the min step in the sweep
            start_step = sweep_index * self.num_steps_per_sweep
            # find the step index for the max step in the sweep
            end_step = (sweep_index + 1) * self.num_steps_per_sweep
            # assign (by convention) the midpoint sample in that sweep to the swept spectrum
            midpoint_sample = cumulative_samples + np.sum(self.num_samples[start_step:end_step]) // 2
            # append the midpoint sample as the assigned sample for the current sweep
            assigned_sample_indices.append(midpoint_sample)
            # add to the cumulative samples how many samples there were in the current sweep we just processed
            cumulative_samples += np.sum(self.num_samples[start_step:end_step])
        # convert the sample indices to seconds by using the sampling interval (the assumed time elapsed between samples)
        return np.array(assigned_sample_indices) * (1 / self.samp_rate)

    def _compute_frequencies(self) -> np.ndarray:
        # prime an empty array to hold the stitched frequency array
        freq_MHz = np.empty(self.num_steps_per_sweep * self.window_size)
        # the steps cover identical frequencies in each sweep, regardless of which sweep
        # finding the unique values in self.center_frequencies essentially returns an array holding the assigned center frequency for each step
        for i, freq in enumerate(np.unique(self.center_frequencies)):
            # populate the (stitched) frequency array with the physical frequency range covered by the current step
            lower_bound = i * self.window_size
            upper_bound = (i + 1) * self.window_size
            freq_MHz[lower_bound:upper_bound] = (self.SFT.f + freq) / 1e6
        # return the stitched frequency array
        return freq_MHz
    

    def _stitch_steps(self, averaged_spectra: np.ndarray) -> np.ndarray:
        # numpy magic to stitch together the steps (and assume time coincidence of the spectrums assigned to each step within a sweep)
        return averaged_spectra.reshape((self.num_full_sweeps, -1)).T
