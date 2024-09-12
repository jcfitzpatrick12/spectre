# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.file_handlers.json.SPECTREConfigHandler import SPECTREConfigHandler

class CaptureConfigHandler(SPECTREConfigHandler):
    def __init__(self, tag: str, **kwargs):
        super().__init__(tag, "capture", **kwargs)
    


    

    
