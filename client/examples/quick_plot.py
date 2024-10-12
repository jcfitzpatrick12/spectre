from datetime import datetime

from spectre.chunks import Chunks
from spectre.cfg import DEFAULT_TIME_FORMAT

def main(tag: str, 
         start_time: str, 
         end_time: str):
    start_datetime = datetime.strptime(start_time, 
                                       DEFAULT_TIME_FORMAT)
    chunks = Chunks(tag, 
                    year=start_datetime.year, 
                    month=start_datetime.month,
                    day=start_datetime.day)
    spectrogram = chunks.get_spectrogram_from_range(start_time, end_time)
    print(f"Frequency resolution {spectrogram.freq_res_MHz * 1e6} [Hz]")
    print(f"Time resolution: {spectrogram.time_res_seconds} [s]")
    spectrogram.quick_plot(time_type = "datetimes", log_norm=True)

if __name__ == "__main__":
    tag = "rsp1a-sweep-example"
    start_time, end_time = "2024-10-12T20:00:00", "2024-10-12T20:10:00"
    main(tag, start_time, end_time)







        
