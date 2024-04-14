import numpy as np

from spectre.chunks.ChunkExt import ChunkExt


class ChunkBin(ChunkExt):
    def __init__(self, chunk_start_time: str, tag: str, chunks_dir: str):
        super().__init__(chunk_start_time, tag, ".bin", chunks_dir)

    def get_IQ_data(self) -> np.ndarray:
        try:
            with open(self.get_path(), "rb") as fh:
                IQ_data = np.fromfile(fh, dtype=np.complex64)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error fetching IQ data, received {e}.")
        return IQ_data