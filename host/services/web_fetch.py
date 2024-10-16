# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import List

from spectre.web_fetch.callisto import fetch_chunks

def callisto(
    instrument_code: str,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
) -> None:
    fetch_chunks(instrument_code, year=year, month=month, day=day)