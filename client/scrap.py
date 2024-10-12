from spectre.file_handlers.chunks.Chunks import Chunks
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.spectrogram.transform import frequency_average

chunks = Chunks("RSP1A-sweeper", year=2024, month=10, day=3)
S = chunks.get_spectrogram_from_range("2024-10-03T12:20:00", "2024-10-03T12:24:00")
S = frequency_average(S, 20)
S.quick_plot(time_type="datetimes", dBb=True, vmax=2)

    








        
