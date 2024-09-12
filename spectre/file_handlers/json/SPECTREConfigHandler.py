# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any
import os

from cfg import (
    JSON_CONFIGS_DIR_PATH
)
from spectre.file_handlers.json.JsonHandler import JsonHandler

class SPECTREConfigHandler(JsonHandler):
    def __init__(self, tag: str, config_type: str, **kwargs):
        self._check_tag(tag)
        self.tag = tag
        self.config_type = config_type
        super().__init__(JSON_CONFIGS_DIR_PATH, f"{config_type}_config_{tag}", **kwargs)
    

    def _check_tag(self, tag: str) -> None:
        if "_" in tag:
            raise ValueError(f"Tags cannot contain an underscore. Received {tag}.")

        if "callisto" in tag:
            raise ValueError(f"\"callisto\" cannot be a substring in a native tag. Received \"{tag}\"")

        return
    
    

