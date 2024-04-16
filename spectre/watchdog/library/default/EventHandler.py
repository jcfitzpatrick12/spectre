import os

from spectre.watchdog.BaseEventHandler import BaseEventHandler
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.watchdog.event_handler_register import register_event_handler

@register_event_handler("default")
class EventHandler(BaseEventHandler):
    def __init__(self, watcher, tag: str, extension: str, chunks_dir: str, json_configs_dir: str):
        super().__init__(watcher, tag, extension, chunks_dir, json_configs_dir)

    def process(self, file_path: str):
        print(f"Processing {file_path}")
        file_name = os.path.basename(file_path)
        chunk_start_time, _ = os.path.splitext(file_name)[0].split('_')
        chunk = self.Chunk(chunk_start_time, self.tag, self.chunks_dir, self.json_configs_dir)
        if chunk:
            time_seconds, freq_MHz, dynamic_spectra = chunk.build_spectrogram()
            S = Spectrogram(dynamic_spectra, time_seconds, freq_MHz, chunk.chunk_start_time, "test", units="amplitude")
            S.save_to_fits(self.chunks_dir, self.json_configs_dir)
            print(f"Processing complete. Removing {file_path}.")
            os.remove(file_path)
        else:
            print(f"Chunk not found for start time {chunk_start_time}. Skipping.")
