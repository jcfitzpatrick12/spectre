# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional

from spectre_core.logging import log_call
from spectre_core.web_fetch.callisto import fetch_chunks
from spectre_core.cfg import CALLISTO_INSTRUMENT_CODES

@log_call
def get_instrument_codes(
) -> list[str]:
    """Get all defined CALLISTO instrument codes"""
    return CALLISTO_INSTRUMENT_CODES


@log_call
def download(
    instrument_code: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> None:
    fetch_chunks(instrument_code, 
                 year,
                 month,
                 day)