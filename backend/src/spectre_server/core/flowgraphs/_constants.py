# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses


@dataclasses.dataclass(frozen=True)
class FlowgraphConstant:
    """Constants across all flowgraphs."""

    GROUP_BY_DATE = True
    NO_INITIAL_TAG_VALUE = 0
