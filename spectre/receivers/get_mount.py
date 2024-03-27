# it is important to import the receivers library
# since the decorators only take effect on import
import spectre.receivers.library
# after we decorate all the mounts, we can import the receiver -> mount mapsw
from spectre.receivers.mount_register import capture_config_mounts, capture_mounts

# fetch a capture config mount for a given receiver name
def get_capture_config_mount(receiver_name: str):
    valid_receivers = list(capture_config_mounts.keys())
    if not receiver_name in valid_receivers:
        raise ValueError(f"No capture config mount found for receiver: {receiver_name}. Please specify one of the following receivers {valid_receivers}.")
    return capture_config_mounts[receiver_name]()


# fetch a capture mount for a given receiver name
def get_capture_mount(receiver_name: str):
    valid_receivers = list(capture_mounts.keys())
    if not receiver_name in valid_receivers:
        raise ValueError(f"No capture mount found for receiver: {receiver_name}. Please specify one of the following receivers {valid_receivers}.")

    return capture_mounts[receiver_name]()
