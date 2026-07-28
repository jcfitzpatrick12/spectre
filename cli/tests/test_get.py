# SPDX-FileCopyrightText: © 2026 w3lld1
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typer.testing import CliRunner

from spectre_cli.__main__ import app
import spectre_cli.commands.get as get_commands


def test_get_receiver(monkeypatch) -> None:
    monkeypatch.setattr(
        get_commands,
        "safe_request",
        lambda route, method: {
            "status": "success",
            "data": {
                "name": "rtlsdr",
                "modes": ["fixed_center_frequency"],
                "found": True,
            },
        },
    )

    result = CliRunner().invoke(app, ["get", "receiver", "--receiver", "rtlsdr"])

    assert result.exit_code == 0
    assert "name: rtlsdr" in result.stdout
    assert "found: true" in result.stdout
