# it is important to import the event handler library
# since the decorators only take effect on import
# this import will run the __init__.py within library, which will dynamically import all the event handlers
import spectre.watchdog.library
from spectre.watchdog.event_handler_register import event_handler_map
from spectre.json_config.CaptureConfig import CaptureConfig

def get_event_handler(event_handler_key: str):
    # try and fetch the capture config mount
    event_handler = event_handler_map.get(event_handler_key)
    if event_handler is None:
        valid_event_handler_keys = list(event_handler_map.keys())
        raise ValueError(f"No chunk found for the event handler key: {event_handler_key}. Please specify one of the following event handler keys {valid_event_handler_keys}.")
    return event_handler

def get_event_handler_from_tag(tag: str, json_configs_dir: str):
    capture_config_instance = CaptureConfig(tag, json_configs_dir)
    capture_config = capture_config_instance.load_as_dict()
    event_handler_key = capture_config.get('event_handler_key', None)
    return get_event_handler(event_handler_key)
