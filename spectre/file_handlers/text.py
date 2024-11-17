# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.file_handlers.base import BaseFileHandler

class TextHandler(BaseFileHandler):
    def __init__(self, 
                 parent_path: str,
                 base_file_name: str, 
                 extension: str = "txt",
                 **kwargs):
        super().__init__(parent_path,
                         base_file_name,
                         extension, 
                         **kwargs)
    

    def read(self) -> dict:
        with open(self.file_path, 'r') as f:
            return f.read()