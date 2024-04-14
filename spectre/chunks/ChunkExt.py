import os

from spectre.utils import datetime_helpers

class ChunkExt:
    def __init__(self, chunk_start_time: str, tag: str, ext: str, chunks_dir: str):
        self.chunk_start_time = chunk_start_time
        self.tag = tag
        self.ext = ext
        self.file = f"{self.chunk_start_time}_{tag}.{self.ext}"
        self.chunk_dir = datetime_helpers.build_chunks_dir(self.chunk_start_time, chunks_dir)


    def get_path(self) -> str:
        return os.path.join(self.chunk_dir, f"{self.chunk_start_time}_{self.tag}{self.ext}")
    

    def exists(self) -> bool:
        return os.path.exists(self.get_path())
    