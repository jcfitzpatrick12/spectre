import numpy as np

def compute_resolution(array: np.array) -> float:
    if len(array) < 2:
        raise ValueError("Input array must contain at least two elements.")
    
    # Calculate differences between consecutive elements.
    resolutions = np.diff(array)
    
    # Verify that resolution is consistent.
    if not np.allclose(resolutions, resolutions[0]):
        raise ValueError("Time resolution is not consistent across all elements.")
    
    return resolutions[0]