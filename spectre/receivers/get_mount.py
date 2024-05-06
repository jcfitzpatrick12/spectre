# it is important to import the receivers library
# since the decorators only take effect on import
# this import will run the __init__.py within library, which will dynamically import all the receivers
import spectre.receivers.library
# after we decorate all the mounts, we can import the receiver -> mount mapsw
from spectre.receivers.mount_register import capture_config_mounts, capture_mounts

from spectre.receivers.BaseCaptureConfigMount import BaseCaptureConfigMount
from spectre.receivers.BaseCaptureMount import BaseCaptureMount

# fetch a capture config mount for a given receiver name
def get_capture_config_mount(receiver_name: str) -> BaseCaptureConfigMount:
    # try and fetch the capture config mount
    Mount = capture_config_mounts.get(receiver_name)
    if Mount is None:
        valid_receivers = list(capture_config_mounts.keys())
        raise ValueError(f"No capture config mount found for receiver: {receiver_name}. Please specify one of the following receivers {valid_receivers}.")
    return Mount


# fetch a capture mount for a given receiver name
def get_capture_mount(receiver_name: str) -> BaseCaptureMount:
    # try and fetch the capture config mount
    Mount = capture_mounts.get(receiver_name)
    if Mount is None:
        valid_receivers = list(capture_config_mounts.keys())
        raise ValueError(f"No capture mount found for receiver: {receiver_name}. Please specify one of the following receivers {valid_receivers}.")
    return Mount

