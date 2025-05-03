# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import date, datetime
from typing import Optional
from os.path import basename

from spectre_core.batches import parse_batch_base_file_name
from spectre_core.logs import parse_log_base_file_name
from spectre_core.config import TimeFormat


def get_date_from_batch_file_path(
    batch_file_path: str
) -> date:
    """Given a batch file path, parse the date it belongs to."""
    base_file_name  = basename(batch_file_path)
    start_time, _, _ = parse_batch_base_file_name(base_file_name)
    return datetime.strptime(start_time, TimeFormat.DATETIME).date()


def get_date_from_log_file_path(
    log_file_path: str
) -> date:
    """Given a batch file path, parse the date it belongs to."""
    base_file_name  = basename(log_file_path)
    start_time, _, _ = parse_log_base_file_name(base_file_name)
    return datetime.strptime(start_time, TimeFormat.DATETIME).date()


def validate_date(
    year: Optional[int]=None,
    month: Optional[int]=None,
    day: Optional[int]=None,
) -> None:
    """
    Validate that the provided date components follow one of the allowed patterns and do not represent a future date.

    Allowed:
    - No values (None, None, None)
    - Year only
    - Year and month
    - Full date (year, month, day)

    Raises:
        ValueError: If components are out of order, invalid, or in the future.
    """
    today = date.today()

    if day is not None and month is None:
        raise ValueError("Day cannot be specified without month.")
    if month is not None and year is None:
        raise ValueError("Month cannot be specified without year.")
    
    # Early exit: no date provided, and no validation is required.
    if year is None:
        return

    try:
        # Fill in default values to construct a date.
        # Makes validation simpler.
        d = day if day is not None else 1
        m = month if month is not None else 1
        constructed = date(year, m, d)
    except ValueError as e:
        raise ValueError(f"Invalid date: {e}")

    if constructed > today:
        raise ValueError("Date cannot be in the future.")
