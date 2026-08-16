# SPDX-FileCopyrightText: © 2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import flask.testing

import spectre_server.services.configs as services

TAG = "cw"
FILE_NAME = f"{TAG}.json"


def test_get_config_locked_returns_batch_state(
    client: flask.testing.FlaskClient, monkeypatch
) -> None:
    monkeypatch.setattr(
        services, "is_config_locked", lambda file_name: file_name == FILE_NAME
    )

    response = client.get(f"/spectre-data/configs/{FILE_NAME}/locked")

    assert response.status_code == 200
    assert response.get_json() == {"status": "success", "data": True}


def test_update_locked_config_returns_user_facing_conflict(
    client: flask.testing.FlaskClient, monkeypatch
) -> None:
    response = client.put(
        f"/spectre-data/configs/{FILE_NAME}",
        json={
            "receiver_name": "signal_generator",
            "receiver_mode": "cosine_wave",
            "validate": False,
        },
    )
    assert response.get_json()["status"] == "success"

    monkeypatch.setattr(services, "is_config_locked", lambda file_name: True)
    response = client.patch(
        f"/spectre-data/configs/{FILE_NAME}",
        json={"params": {"time_range": "1.0"}, "validate": False},
    )

    assert response.status_code == 409
    jsend = response.get_json()
    assert jsend["status"] == "error"
    assert "locked" in jsend["message"]
    assert "force" in jsend["message"]
