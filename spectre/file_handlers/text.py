# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.file_handlers.base import BaseFileHandler

class TextHandler(BaseFileHandler):
    def __init__(self, *args, **kwargs):
        if "extension" in kwargs:
            raise ValueError("The 'extension' cannot be specified - it is fixed to 'txt'. Please use override_extension if required")
        super().__init__(*args, extension = "txt", **kwargs)
        return 
    
    def read(self) -> dict:
        with open(self.file_path, 'r') as f:
            return f.read()