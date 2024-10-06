from spectre.file_handlers.chunks.Chunks import Chunks
from spectre.spectrogram.Spectrogram import Spectrogram

if __name__ == "__main__":
     chunks = Chunks("RSPduo-tuner-1-sweep-example", year=2024, month=10, day=5)
     for chunk in chunks:
         if chunk.has_file("fits"):
             fits_chunk = chunk.get_file("fits")
             spectrogram = fits_chunk.read()
             spectrogram.quick_plot(log_norm=True)
    








        
