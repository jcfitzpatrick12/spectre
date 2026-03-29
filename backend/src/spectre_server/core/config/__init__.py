# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


"""Program-wide config."""

from ._paths import paths, Paths
from ._time_formats import TimeFormat

__all__ = ["paths", "Paths", "TimeFormat"]
