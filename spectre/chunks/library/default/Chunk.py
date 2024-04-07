
import numpy as np
from typing import Tuple
from scipy.signal import ShortTimeFFT, get_window

from spectre.chunks.ChunkBase import ChunkBase
from spectre.chunks.chunk_register import register_chunk
from spectre.utils import json_helpers

from spectre.chunks.library.default.ChunkBin import ChunkBin
from spectre.chunks.library.default.ChunkFits import ChunkFits


@register_chunk('default')
class Chunk(ChunkBase):
    #constructor for SingleFileHandler
    def __init__(self, chunk_start_time: str, tag: str, chunks_dir: str):
        super().__init__(chunk_start_time, tag, chunks_dir) 

        self.bin = ChunkBin(chunk_start_time, tag, chunks_dir)
        self.fits = ChunkFits(chunk_start_time, tag, chunks_dir)


    def build_radio_spectrogram(self, json_configs_dir: str) -> Tuple[np.array, np.array, np.array]:
        if not self.bin.exists():
            raise FileNotFoundError(f"Cannot build spectrogram, {self.bin.get_path()} does not exist.")
        # load the capture config for the current tag
        capture_config = json_helpers.load_json_as_dict(f"capture_config_{self.tag}", json_configs_dir)

        # fetch the window
        w = self.fetch_window(capture_config)

        time_seconds, freq_MHz, mags = self.do_STFFT(capture_config, w)

        # convert all arrays to standard type
        time_seconds = np.array(time_seconds, dtype = 'float64')
        freq_MHz = np.array(freq_MHz, dtype = 'float64')
        mags = np.array(mags, dtype = 'float64')

        return time_seconds, freq_MHz, mags

    
    def fetch_window(self, capture_config: dict) -> np.array:
        # fetch the window params and get the appropriate window
        window_type = capture_config.get('window_type')
        window_kwargs = capture_config.get('window_kwargs')
        window_params = (window_type, *window_kwargs.values())
        Nx = capture_config.get('Nx')
        w = get_window(window_params, Nx)
        return w
    

    def do_STFFT(self, capture_config: dict, w: np.array) -> Tuple[np.array, np.array, np.array]:
        # fetch the IQ data
        IQ_data = self.bin.get_IQ_data()
        samp_rate = capture_config.get('samp_rate')
        # fetch the STFFT kwargs
        STFFT_kwargs = capture_config.get('STFFT_kwargs')
        # perform the short time FFT (specifying explicately keywords centered and magnitude)
        SFT = ShortTimeFFT(w, fs=samp_rate, fft_mode='centered', scale_to='magnitude', **STFFT_kwargs)
        Sx = SFT.stft(IQ_data)  # perform the STFT
        mags = abs(Sx)

        # find the number of samples 
        num_samples = len(IQ_data)
        # build the time array
        time_seconds = SFT.t(num_samples) # seconds

        # fetch the center_freq (if not specified, defaults to zero)
        center_freq = capture_config.get('center_freq', 0)
        # build the frequency array
        frequency_array = SFT.f + center_freq # Hz
        freq_MHz = frequency_array / 10**6

        return time_seconds, freq_MHz, mags




