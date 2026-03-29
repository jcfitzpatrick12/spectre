# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from enum import Enum


class ProcessType(Enum):
    """The origin of a Spectre process.

    USER: The main user session.
    WORKER: A background task created and managed internally by Spectre.
    """

    USER = "user"
    WORKER = "worker"
