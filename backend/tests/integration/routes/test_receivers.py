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


def test_find_receiver(client: flask.testing.FlaskClient) -> None:
    response = client.get("/receivers/signal_generator/found")
    assert response.get_json() == {"status": "success", "data": True}


def test_get_modes(client: flask.testing.FlaskClient) -> None:
    response = client.get("/receivers/signal_generator/modes")
    assert response.get_json() == {
        "status": "success",
        "data": ["cosine_wave", "constant_staircase"],
    }
