templates = {
    "fixed": {
        "center_freq": float,
        "bandwidth": float,
        "samp_rate": int, 
        "IF_gain": int,
        "RF_gain": int,
        "chunk_size": int,
        "integration_time": int,
    },
    'sweeping': {
        "center_freq": float,
        "samp_rate": int,
        "IF_gain": int,
        "RF_gain": int,
        "chunk_size": int,
        "swept_bandwidth": float,
        "frequency_step": float,
        "sweep_window": float,
        "integration_time": float,
    },
}