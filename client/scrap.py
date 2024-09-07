from spectre.chunks.Chunks import Chunks
from spectre.spectrogram.transform import (
    join_spectrograms,
    frequency_chop
)

chunks = Chunks("RSP1A-sweeper", year=2024, month=9, day=7)

# start_time = "2024-09-07T14:46:00"
# end_time =  "2024-09-07T14:47:00"
# S = chunks.build_spectrogram_from_range(start_time, end_time)

spectrograms = [chunk.fits.read() for chunk in chunks if chunk.fits.exists()]
S = join_spectrograms(spectrograms)
S.quick_plot(dBb=True)
print(S.time_res_seconds)
        
