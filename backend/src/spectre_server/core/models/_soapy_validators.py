# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from ._validators import validate_one_of

EXPECTED_OUTPUT_TYPES: list[str] = ["fc32", "sc16", "sc8"]


def validate_output_type(output_type: str):
    """Checks the output type is supported."""
    validate_one_of(output_type, EXPECTED_OUTPUT_TYPES, "output_type")
