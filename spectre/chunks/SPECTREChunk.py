from abc import ABC, abstractmethod

from spectre.chunks.BaseChunk import BaseChunk
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.json_config.CaptureConfigHandler import CaptureConfigHandler


class SPECTREChunk(BaseChunk):
    def __init__(self, chunk_start_time: str, tag: str):
        super().__init__(chunk_start_time, tag)
        
        capture_config_handler = CaptureConfigHandler(tag)
        self.capture_config = capture_config_handler.load_as_dict()
    
    
    @abstractmethod
    def build_spectrogram(self) -> Spectrogram:
        pass