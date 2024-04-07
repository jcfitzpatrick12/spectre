import numpy as np
import os
from datetime import datetime

from spectre.utils import datetime_helpers, array_helpers, fits_helpers
from spectre.utils import fits_helpers
from spectre.cfg import CONFIG


class Spectrogram:
    def __init__(self, 
                 mags: np.array,
                 time_seconds: np.array, 
                 freq_MHz: np.array, 
                 chunk_start_time: str, 
                 tag: str, 
                 chunks_dir: str,
                 **kwargs):
        self.mags = mags
        self.time_seconds = time_seconds
        self.freq_MHz = freq_MHz
        self.chunk_start_time = chunk_start_time
        self.tag = tag
        self.chunks_dir = datetime_helpers.build_chunks_dir(self.chunk_start_time, chunks_dir) 
        self.bvect = kwargs.get("bvect", None)

        self.chunk_start_datetime = datetime.strptime(self.chunk_start_time, CONFIG.default_time_format)
        self.datetime_array = datetime_helpers.build_datetime_array(self.chunk_start_datetime, time_seconds)

        self.time_res_seconds = array_helpers.compute_resolution(time_seconds)
        self.freq_res_MHz = array_helpers.compute_resolution(freq_MHz)


    def get_path(self) -> str:
        return os.path.join(self.chunks_dir,f"{self.chunk_start_time}_{self.tag}.fits")


    def save_to_fits(self, fits_config: dict) -> None:
        fits_helpers.save_spectrogram(self, fits_config, self.get_path())
        return
