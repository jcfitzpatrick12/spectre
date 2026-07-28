# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess

import pytest

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
        "rx888mk2",
    ]


def test_discover_receiver_reports_command_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def run(command: list[str], **kwargs) -> subprocess.CompletedProcess:
        assert command == ["SoapySDRUtil", "--probe=driver=rtlsdr"]
        assert kwargs == {"capture_output": True, "check": False}
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", run)

    assert services.discover_receiver("rtlsdr") == {
        "name": "rtlsdr",
        "modes": ["fixed_center_frequency"],
        "found": True,
    }


def test_discover_receiver_reports_missing_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def run(command: list[str], **kwargs) -> subprocess.CompletedProcess:
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", run)

    assert services.discover_receiver("rtlsdr")["found"] is False
