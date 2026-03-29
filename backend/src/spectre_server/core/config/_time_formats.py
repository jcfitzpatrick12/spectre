# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeFormat:
    """Package-wide datetime formats.

    :ivar DATE: Format for dates (e.g., '2025-01-11').
    :ivar TIME: Format for times (e.g., '23:59:59').
    :ivar FRACTIONAL_TIME: Format for times with microsecond precision (e.g., '23:59:59.123456')
    :ivar DATETIME: Format for datetimes compliant with the ISO-8601 standard (e.g., '2025-01-11T23:59:59.123456Z')
    """

    DATE = "%Y-%m-%d"
    TIME = "%H:%M:%S"
    FRACTIONAL_TIME = "%H:%M:%S.%f"
    DATETIME = f"{DATE}T{FRACTIONAL_TIME}Z"
