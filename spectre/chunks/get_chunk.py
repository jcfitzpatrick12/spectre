# it is important to import the chunks library
# since the decorators only take effect on import
# this import will run the __init__.py within library, which will dynamically import all the receivers
import spectre.chunks.library
# after we decorate all chunks, we can import the chunk_key -> chunk maps
from spectre.chunks.chunk_register import chunk_map

# fetch a capture config mount for a given receiver name
def get_chunk(chunk_key: str):
    # try and fetch the capture config mount
    chunk = chunk_map.get(chunk_key)
    if chunk is None:
        valid_chunk_keys = list(chunk_map.keys())
        raise ValueError(f"No chunk found for the chunk key: {chunk_key}. Please specify one of the following receivers {valid_chunk_keys}.")
    return chunk