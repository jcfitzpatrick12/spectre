import json
import os
from spectre.utils import file_helpers


def save_dict_as_json(data_dict: dict, name: str, dir_path: str, doublecheck_overwrite=True) -> None:
    """
    """
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
        # raise NotADirectoryError(f"The directory '{dir_path}' does not exist.")

    fpath = os.path.join(dir_path, f"{name}.json")

    if os.path.exists(fpath) and doublecheck_overwrite:
        file_helpers.doublecheck_overwrite_at_path(fpath)
        
    try:
        with open(fpath, 'w') as json_file:
            json.dump(data_dict, json_file, indent=4)
        # print(f"File '{fpath}' has been saved successfully.")
    except (IOError, PermissionError) as e:
        raise RuntimeError(f"Failed to save '{fpath}': {e}") from e




def load_json_as_dict(name: str, dir_path: str) -> dict:
    """

    """
    if not os.path.exists(dir_path):
        # change this to a IsNotDirectory error
        raise NotADirectoryError(f"The directory {dir_path} does not exist.")
    
    fpath = os.path.join(dir_path, f"{name}.json")

    try:
        with open(fpath, 'r') as json_file:
            return json.load(json_file)
    
    except FileNotFoundError:
        raise FileNotFoundError(f"File does not exist: {fpath}")
    except IOError as e:
        raise IOError(f"Error reading file: {fpath}") from e
 
    
        
    