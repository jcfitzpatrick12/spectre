from datetime import datetime
from spectre.cfg import CONFIG
from spectre.utils import datetime_helpers

class ChunkBase:
    def __init__(self, chunk_start_time: str, tag: str, chunks_dir: str):
        self.chunk_start_time = chunk_start_time
        self.tag = tag
        try:
            self.chunk_start_datetime = datetime.strptime(self.chunk_start_time, CONFIG.default_time_format)
        except ValueError as e:
            raise ValueError(f"Could not parse {chunk_start_time}, received {e}.")
        
        self.chunks_dir = datetime_helpers.build_chunks_dir(self.chunk_start_time, chunks_dir)