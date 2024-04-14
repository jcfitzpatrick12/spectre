
import numpy as np
from typing import Tuple
from scipy.signal import ShortTimeFFT, get_window
import matplotlib.pyplot as plt

from spectre.chunks.ChunkBase import ChunkBase
from spectre.chunks.chunk_register import register_chunk
from spectre.utils import json_helpers

from spectre.chunks.library.default.ChunkBin import ChunkBin
from spectre.chunks.library.default.ChunkFits import ChunkFits


@register_chunk('default')
class Chunk(ChunkBase):
    def __init__(self, chunk_start_time: str, tag: str, chunks_dir: str, json_configs_dir: str):
        super().__init__(chunk_start_time, tag, chunks_dir, json_configs_dir) 

        self.bin = ChunkBin(chunk_start_time, tag, chunks_dir)
        self.fits = ChunkFits(chunk_start_time, tag, chunks_dir)


    def build_spectrogram(self) -> Tuple[np.array, np.array, np.array]:
        if not self.bin.exists():
            raise FileNotFoundError(f"Cannot build spectrogram, {self.bin.get_path()} does not exist.")
        # load the capture config for the current tag
        capture_config = json_helpers.load_json_as_dict(f"capture_config_{self.tag}", self.json_configs_dir)

        # fetch the window
        w = self.fetch_window(capture_config)

        time_seconds, freq_MHz, mags = self.do_STFFT(capture_config, w)

        # convert all arrays to the standard type
        time_seconds = np.array(time_seconds, dtype = 'float64')
        freq_MHz = np.array(freq_MHz, dtype = 'float64')
        mags = np.array(mags, dtype = 'float64')

        return time_seconds, freq_MHz, mags

    
    def fetch_window(self, capture_config: dict) -> np.ndarray:
        # fetch the window params and get the appropriate window
        window_type = capture_config.get('window_type')
        window_kwargs = capture_config.get('window_kwargs')
        window_params = (window_type, *window_kwargs.values())
        Nx = capture_config.get('Nx')
        w = get_window(window_params, Nx)
        return w
    

    def do_STFFT(self, capture_config: dict, w: np.ndarray) -> Tuple[np.array, np.array, np.array]:
        '''
        For reference: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.ShortTimeFFT.html
        '''

        # fetch the IQ data
        IQ_data = self.bin.get_IQ_data()
        # find the number of samples 
        num_samples = len(IQ_data)
        # fetch the sample rate
        samp_rate = capture_config.get('samp_rate')
        # fetch the STFFT kwargs
        STFFT_kwargs = capture_config.get('STFFT_kwargs')

        # perform the short time FFT (specifying explicately keywords centered and magnitude)
        SFT = ShortTimeFFT(w, fs=samp_rate, fft_mode='centered', **STFFT_kwargs)
        # SFT = ShortTimeFFT(w, fs=samp_rate, **STFFT_kwargs)

        # set p0=0, since by convention in the STFFT docs, p=0 corresponds to the slice centred at t=0
        p0=0
        # set p1=p_ub, the index of the first slice where the "midpoint" of the window is still inside the signal
        p_ub = SFT.upper_border_begin(num_samples)[1]
        p1=p_ub
        
        signal_spectra = SFT.stft(IQ_data, p0=p0, p1=p1)  # perform the STFT (no scaling)
        # take the magnitude of the output
        mags = np.abs(signal_spectra)

        # build the time array
        time_seconds = SFT.t(num_samples, p0=0, p1=p1) # seconds

        # fetch the center_freq (if not specified, defaults to zero)
        center_freq = capture_config.get('center_freq', 0)
        # build the frequency array
        frequency_array = SFT.f + center_freq # Hz
        # convert the frequency array to MHz
        freq_MHz = frequency_array / 10**6

        return time_seconds, freq_MHz, mags




