def fixed_validator(capture_config_dict):
    center_freq = capture_config_dict['center_freq']
    bandwidth = capture_config_dict['bandwidth']
    samp_rate = capture_config_dict['samp_rate']
    IF_gain = capture_config_dict['IF_gain']
    RF_gain = capture_config_dict['RF_gain']
    chunk_size = capture_config_dict['chunk_size']
    integration_time = capture_config_dict['integration_time']

    validate_center_freq(center_freq)
    validate_bandwidth(bandwidth, samp_rate)
    validate_samp_rate(bandwidth, samp_rate)
    validate_IF_gain(IF_gain)
    validate_RF_gain(RF_gain)
    validate_chunk_size(chunk_size)
    validate_integration_time(integration_time, chunk_size)
    pass


def sweeping_validator(capture_config_dict):
    pass


def validate_center_freq(proposed_center_freq):
    if proposed_center_freq <= 0:
        raise ValueError(f"Center frequency must be non-negative. Received {proposed_center_freq}")
    pass


def validate_bandwidth(proposed_bandwidth, proposed_samp_rate):
    if proposed_samp_rate < proposed_bandwidth:
        raise ValueError(f"Sample rate must be greater than or equal to the bandwidth.")
    pass


def validate_samp_rate(proposed_bandwidth, proposed_samp_rate):
    if proposed_samp_rate < proposed_bandwidth:
        raise ValueError("Sample rate must be greater than or equal to the bandwidth.")
    pass


def validate_RF_gain(RF_gain):
    if RF_gain > 0:
        raise ValueError(f"RF_gain must non-positive. Received {RF_gain}.")
    pass

def validate_IF_gain(IF_gain):
    if IF_gain > 0:
        raise ValueError(f"IF_gain must non-positive. Received {IF_gain}.")
    pass


def validate_chunk_size(chunk_size):
    pass


def validate_integration_time(integration_time, chunk_size):
    if integration_time > chunk_size:
        raise ValueError(f'Integration time cannot be greater than chunk_size.')
    pass