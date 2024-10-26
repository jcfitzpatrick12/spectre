# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.spectrograms.spectrogram import Spectrogram
from spectre.plotting.base import BasePanel
from spectre.plotting.panel_register import panels
from spectre.exceptions import PanelNotFoundError

def get_panel(panel_name: str, 
              spectrogram: Spectrogram,
              time_type: str,
              *args, 
              **kwargs) -> BasePanel:
    try:
        Panel = panels[panel_name]
        return Panel(spectrogram, 
                     time_type,
                     *args, 
                     **kwargs)
    except KeyError:
        valid_panels = list(panels.keys())
        raise PanelNotFoundError(f"Could not find panel with name {panel_name}. "
                                 f"Expected one of {valid_panels}")
