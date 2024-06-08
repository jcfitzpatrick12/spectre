# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from spectre.json_config.JsonConfigHandler import JsonConfigHandler

class CaptureConfigHandler(JsonConfigHandler):
    def __init__(self, tag: str):
        super().__init__("capture", tag)
    


    

    
