# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from math import floor
from typing import Optional

from spectre.receivers.SPECTREReceiver import SPECTREReceiver

# parent class for shared methods and attributes of SDRPlay receivers
class SDRPlayReceiver(SPECTREReceiver):
    def __init__(self, receiver_name: str, mode: str = None):
        super().__init__(receiver_name, mode = mode)
        self.api_latency = 50 * 1e-3 # [s]