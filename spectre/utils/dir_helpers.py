# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import warnings


def list_all_files(parent_dir: str):
        if not os.path.exists(parent_dir):
            raise NotADirectoryError(f"Could not find {parent_dir}.")
        
        all_files = []
        #walk through all the subdirectories in data
        for root, dirs, files in os.walk(parent_dir):
            for file in files:
                all_files.append(file)
        
        if len(all_files) == 0:
            warnings.warn(f"No files identified within {parent_dir}", UserWarning)
            
        return all_files

