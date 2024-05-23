from spectre.chunks.BaseChunk import BaseChunk
from spectre.chunks.chunk_register import register_chunk

from spectre.chunks.library.callisto.ChunkFits import ChunkFits


@register_chunk('callisto')
class Chunk(BaseChunk):
    def __init__(self, chunk_start_time: str, tag: str):
        super().__init__(chunk_start_time, tag) 
        self.fits = ChunkFits(chunk_start_time, tag)




