from spectre.utils import json_helpers

def main(capture_config_dict: dict) -> None:
    print("Dummy sweeping capture using capture config:\n")
    json_helpers.print_config(capture_config_dict)
    return 
