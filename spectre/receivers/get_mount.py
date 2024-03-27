# it is important to import the receivers library
# since the decorators only take effect on import
import spectre.receivers.library
# after we decorate all the mounts, we can import the receiver -> mount mapsw
from spectre.receivers.mount_register import capture_config_mounts, capture_mounts

# fetch a capture config mount for a given receiver name
def get_capture_config_mount(receiver_name: str):
    # try and fetch the capture config mount
    capture_config_mount = capture_config_mounts.get(receiver_name)
    if capture_config_mount is None:
        valid_receivers = list(capture_config_mounts.keys())
        raise ValueError(f"No capture config mount found for receiver: {receiver_name}. Please specify one of the following receivers {valid_receivers}.")
    # if found, return an instance of the class
    try:
        return capture_config_mount()
    except TypeError as e:
        raise TypeError(f"Failed to create instance of capture config mount for receiver {receiver_name}. Received the error: {e}")


# fetch a capture mount for a given receiver name
def get_capture_mount(receiver_name: str):
    # try and fetch the capture config mount
    capture_mount = capture_mounts.get(receiver_name)
    if capture_mount is None:
        valid_receivers = list(capture_config_mounts.keys())
        raise ValueError(f"No capture mount found for receiver: {receiver_name}. Please specify one of the following receivers {valid_receivers}.")
    # if found, return an instance of the class
    try:
        return capture_mount()
    except TypeError as e:
            raise TypeError(f"Failed to create instance of capture mount for receiver {receiver_name}. Received the error: {e}")
