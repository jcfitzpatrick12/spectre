# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os
from pathlib import Path

from spectre.utils import file_helpers


def save_dict_as_json(d: dict, file_path: str, doublecheck_overwrite=True) -> None:
    parent_path = Path(file_path).parent
    if not os.path.exists(parent_path):
        os.mkdir(parent_path)

    if os.path.exists(file_path) and doublecheck_overwrite:
        file_helpers.doublecheck_overwrite_at_path(file_path)
        
    try:
        with open(file_path, 'w') as file:
            json.dump(d, file, indent=4)

    except (IOError, PermissionError) as e:
        raise RuntimeError(f"Failed to save '{file_path}': {e}") from e


def load_json_as_dict(file_path: str) -> dict:

    parent_path = Path(file_path).parent
    if not os.path.exists(parent_path):
        os.mkdir(parent_path)

    try:
        with open(file_path, 'r') as json_file:
            return json.load(json_file)
    
    except FileNotFoundError:
        raise FileNotFoundError(f"File does not exist: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading file: {file_path}") from e
 
    
        
    