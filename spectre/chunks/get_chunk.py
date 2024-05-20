# it is important to import the chunks library
# since the decorators only take effect on import
# this import will run the __init__.py within library, which will dynamically import all the chunks
import spectre.chunks.library
# after we decorate all chunks, we can import the chunk_key -> chunk maps
from spectre.chunks.chunk_register import chunk_map
from spectre.chunks.BaseChunk import BaseChunk
from spectre.json_config.CaptureConfigHandler import CaptureConfigHandler

def get_chunk(chunk_key: str) -> BaseChunk:
    chunk = chunk_map.get(chunk_key)
    if chunk is None:
        valid_chunk_keys = list(chunk_map.keys())
        raise ValueError(f"No chunk found for the chunk key: {chunk_key}. Please specify one of the following chunk keys {valid_chunk_keys}.")
    return chunk

def get_chunk_from_tag(tag: str) -> BaseChunk:
    # if we are dealing with a callisto chunk, the chunk key is equal to the tag
    if "callisto" in tag:
        chunk_key = "callisto"
    # otherwise, we fetch the chunk key from the capture config
    else:
        capture_config_handler = CaptureConfigHandler(tag)
        capture_config = capture_config_handler.load_as_dict()
        chunk_key = capture_config.get('chunk_key', None)
    return get_chunk(chunk_key)
