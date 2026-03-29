# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""An API for plotting spectrogram data."""

from ._format import PanelFormat
from ._base import BasePanel, BaseTimeSeriesPanel, XAxisType
from ._panels import (
    SpectrogramPanel,
    FrequencyCutsPanel,
    TimeCutsPanel,
    IntegralOverFrequencyPanel,
)
from ._panel_names import PanelName
from ._panel_stack import PanelStack

__all__ = [
    "BaseTimeSeriesPanel",
    "XAxisType",
    "BasePanel",
    "PanelFormat",
    "PanelStack",
    "PanelName",
    "SpectrogramPanel",
    "FrequencyCutsPanel",
    "TimeCutsPanel",
    "IntegralOverFrequencyPanel",
]
