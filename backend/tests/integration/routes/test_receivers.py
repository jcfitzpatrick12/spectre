# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import flask.testing

import spectre_server.services.receivers as services


def test_get_receivers(client: flask.testing.FlaskClient) -> None:
    response = client.get("/receivers")
    jsend = response.get_json()
    assert jsend["status"] == "success"
    assert isinstance(jsend["data"], list)
    assert "signal_generator" in jsend["data"]


def test_discover_receiver(client: flask.testing.FlaskClient, monkeypatch) -> None:
    expected = {
        "name": "rtlsdr",
        "modes": ["fixed_center_frequency"],
        "found": True,
    }
    monkeypatch.setattr(services, "discover_receiver", lambda receiver_name: expected)

    response = client.get("/receivers/rtlsdr")

    assert response.status_code == 200
    assert response.get_json() == {"status": "success", "data": expected}
