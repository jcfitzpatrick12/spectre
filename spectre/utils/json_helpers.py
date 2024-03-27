import json
import os
import importlib
import pkgutil 


def print_config(config_dict: str) -> None:
    for key, value in config_dict.items():
        print(f"{key}: {value}")
    return


def doublecheck_delete(fpath: str) -> None:
    proceed_with_delete = False
    while not proceed_with_delete:
        user_input = input(f"Are you sure you would like to delete '{fpath}'? [y/n]: ").strip().lower()
        if user_input == "y":
            proceed_with_delete = True
        elif user_input == "n":
            print("Operation cancelled by the user.")
            raise exit(1)
        else:
            print(f"Please enter one of [y/n], received {user_input}.")
            proceed_with_delete = False


def doublecheck_overwrite_at_path(fpath: str) -> None:
    proceed_with_overwrite = False
    while not proceed_with_overwrite:
        user_input = input(f"The file '{fpath}' already exists. Overwrite? [y/n]: ").strip().lower()
        if user_input == "y":
            proceed_with_overwrite = True
        elif user_input == "n":
            print("Operation cancelled by the user.")
            raise exit(1)
        else:
            print(f"Please enter one of [y/n], received {user_input}.")
            proceed_with_overwrite = False


def save_dict_as_json(data_dict: dict, name: str, dir_path: str, **kwargs) -> None:
    """
    """
    doublecheck_overwrite = kwargs.get('doublecheck_overwrite', True)

    if not os.path.exists(dir_path):
        raise NotADirectoryError(f"The directory '{dir_path}' does not exist.")

    fpath = os.path.join(dir_path, f"{name}.json")

    if os.path.exists(fpath) and doublecheck_overwrite:
        doublecheck_overwrite_at_path(fpath)
        
    try:
        with open(fpath, 'w') as json_file:
            json.dump(data_dict, json_file, indent=4)
        print(f"File '{fpath}' has been saved successfully.")
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
    