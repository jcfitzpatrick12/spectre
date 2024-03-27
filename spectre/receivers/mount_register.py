# Global dictionaries to hold the mappings
capture_config_mounts = {}
capture_mounts = {}

# classes decorated with @capture_config_mount("receiver_name")
# will be added to the global map of capture_config_mounts with key "receiver_name"
def register_capture_config_mount(receiver_name: str):
    def decorator(cls):
        capture_config_mounts[receiver_name] = cls
        return cls
    return decorator

# classes decorated with @capture_mount("receiver_name")
# will be added to the global map of capture_mounts with key "receiver_name"
def register_capture_mount(receiver_name: str):
    def decorator(cls):
        capture_mounts[receiver_name] = cls
        return cls
    return decorator
