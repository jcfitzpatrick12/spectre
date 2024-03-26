# Global dictionaries to hold the mappings
capture_config_mounts = {}
capture_mounts = {}

# classes decorated with @capture_config_mount("receiver_name")
# will be added to the global map of capture_config_mounts with key "receiver_name"
def register_capture_config_mount(receiver_name):
    def decorator(cls):
        capture_config_mounts[receiver_name] = cls
        return cls
    return decorator

# classes decorated with @capture_mount("receiver_name")
# will be added to the global map of capture_mounts with key "receiver_name"
def register_capture_mount(receiver_name):
    def decorator(cls):
        capture_mounts[receiver_name] = cls
        return cls
    return decorator


# fetch a capture config mount for a given receiver name
def get_capture_config_mount(receiver_name):
    if receiver_name in capture_config_mounts:
        return capture_config_mounts[receiver_name]()
    else:
        raise ValueError(f"Capture config for {receiver_name} not found.")

# fetch a capture mount for a given receiver name
def get_capture_mount(receiver_name):
    if receiver_name in capture_mounts:
        return capture_mounts[receiver_name]()
    else:
        raise ValueError(f"Capture mount for {receiver_name} not found.")
