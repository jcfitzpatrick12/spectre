# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional

from spectre_core.logging import log_call
from spectre_core import wget
from spectre_core.constants import CALLISTO_INSTRUMENT_CODES

@log_call
def get_instrument_codes(
) -> list[str]:
    """Get all defined CALLISTO instrument codes"""
    return CALLISTO_INSTRUMENT_CODES


@log_call
def download_callisto_data(
    instrument_code: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> None:
    wget.download_callisto_data(instrument_code, 
                                year,
                                month,
                                day)