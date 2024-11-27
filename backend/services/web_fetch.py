# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import Optional

from spectre_radio.web_fetch.callisto import fetch_chunks
from spectre_radio.logging import log_call


@log_call(_LOGGER)
def callisto(
    instrument_code: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> None:
    fetch_chunks(instrument_code, year=year, month=month, day=day)