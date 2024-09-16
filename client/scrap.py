import matplotlib.pyplot as plt
import numpy as np

from spectre.chunks.Chunks import Chunks
from spectre.spectrogram.transform import (
    join_spectrograms,
    frequency_chop,
    time_average,
)

chunks = Chunks("RSP1A-fixed-example", year=2024, month=9, day=11)

for chunk in chunks:
    if chunk.fits.exists():
        S = chunk.fits.read()
        S.quick_plot(log_norm=True)

# spectrograms = [chunk.fits.read() for chunk in chunks if chunk.fits.exists()]
# S = join_spectrograms(spectrograms)
# print(f"Time resolution {S.time_res_seconds} [s]")
# print(f"Frequency resolution {S.freq_res_MHz*1e3} [kHz]")
# print(f"Frequency range {S.freq_MHz[-1] - S.freq_MHz[0]} [MHz]")
# S.quick_plot(log_norm=True)







        
