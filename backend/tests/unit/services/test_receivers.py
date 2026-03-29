# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import spectre_server.services.receivers as services


def test_get_receivers() -> None:
    """Ensure we properly list all supported receivers."""
    result = services.get_receivers()
    assert result == [
        "signal_generator",
        "custom",
        "rsp1a",
        "rspduo",
        "rspdx",
        "usrp",
        "b200mini",
        "hackrf",
        "hackrfone",
        "rtlsdr",
        "rsp1b",
    ]
