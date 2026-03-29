# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import flask.testing


def test_get_receivers(client: flask.testing.FlaskClient) -> None:
    response = client.get("/receivers")
    jsend = response.get_json()
    assert jsend["status"] == "success"
    assert isinstance(jsend["data"], list)
    assert "signal_generator" in jsend["data"]
