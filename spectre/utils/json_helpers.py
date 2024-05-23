import json
import os


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


def save_dict_as_json(data_dict: dict, name: str, dir_path: str, doublecheck_overwrite=True) -> None:
    """
    """
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
        # raise NotADirectoryError(f"The directory '{dir_path}' does not exist.")

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
    
def delete_json_config(json_config_instance, json_config_label: str) -> None:
    if not isinstance(json_config_label, str):
        raise ValueError(f"Expected string for json_config_label, received {type(json_config_label)}")
    
    valid_json_config_labels = ["capture_config", "fits_config"]
    if json_config_label not in valid_json_config_labels:
        raise ValueError(f"Invalid json_config_label. Received {json_config_label}, expected one of {valid_json_config_labels}.")

    config_path = json_config_instance.absolute_path()

    if not os.path.exists(config_path):
        raise FileNotFoundError(f'Could not delete of type {json_config_label} with tag {json_config_instance.tag}. {config_path} does not exist.')
    
    else:
        doublecheck_delete(config_path)
        os.remove(config_path)
        
    