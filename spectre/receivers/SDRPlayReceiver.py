# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from math import floor
from typing import Optional

from spectre.receivers.SPECTREReceiver import SPECTREReceiver

# optional parent class which provides default templates and validators
class SDRPlayReceiver(SPECTREReceiver):
    def __init__(self, receiver_name: str, mode: str = None):
        super().__init__(receiver_name, mode = mode)
        self.api_latency = 50 * 1e-3