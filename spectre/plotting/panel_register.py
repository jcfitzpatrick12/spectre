# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


# Global dictionaries to hold the mappings
panels = {}
    
def register_panel(panel_name: str): 
    def decorator(cls):
        panels[panel_name] = cls
        return cls
    return decorator