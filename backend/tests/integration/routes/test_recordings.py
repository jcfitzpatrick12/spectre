# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import time

import flask.testing


def test_spectrogram_recording_lifecycle(
    client: flask.testing.FlaskClient,
) -> None:
    """Create a spectrogram recording, verify it's running, stop it, and delete it."""

    # Create a default config.
    response = client.put(
        "/spectre-data/configs/cw.json",
        json={
            "receiver_name": "signal_generator",
            "receiver_mode": "cosine_wave",
            "validate": False,
        },
    )
    jsend = response.get_json()
    assert jsend["status"] == "success", jsend

    # Start a recording.
    response = client.post(
        "/recordings/",
        json={
            "tag": "cw",
            "kind": "spectrogram",
            "duration": 60.0,
            "validate": False,
        },
    )
    jsend = response.get_json()
    assert jsend["status"] == "success", jsend
    recording_url = jsend["data"]

    # Give the background thread a moment to start the workers.
    time.sleep(1)

    # Check it's running.
    response = client.get(recording_url)
    jsend = response.get_json()
    assert jsend["status"] == "success", jsend
    assert jsend["data"]["state"] == "running"
    assert jsend["data"]["stop_requested"] is False

    # Request it to stop.
    response = client.patch(recording_url, json={"stop_requested": True})
    jsend = response.get_json()
    assert jsend["status"] == "success", jsend

    # Give the monitor loop a tick to observe the stop request and kill workers.
    time.sleep(1)

    # Check it's stopped.
    response = client.get(recording_url)
    jsend = response.get_json()
    assert jsend["status"] == "success", jsend
    assert jsend["data"]["state"] == "completed"
    assert jsend["data"]["stop_requested"] is True

    # Delete the recording.
    response = client.delete(recording_url)
    jsend = response.get_json()
    assert jsend["status"] == "success", jsend

    # Confirm it's gone.
    response = client.get(recording_url)
    jsend = response.get_json()
    assert jsend["status"] == "error"


def test_recording_fails_without_config(
    client: flask.testing.FlaskClient,
) -> None:
    """A recording whose tag has no config should transition to failed, then be deletable."""

    # Start the recording — no config created for "no-such-tag".
    response = client.post(
        "/recordings/",
        json={
            "tag": "no-such-tag",
            "kind": "spectrogram",
            "duration": 60.0,
        },
    )
    jsend = response.get_json()
    assert jsend["status"] == "success", jsend
    recording_url = jsend["data"]

    # Give the background thread a moment to attempt startup and fail.
    time.sleep(2)

    # Check it's failed.
    response = client.get(recording_url)
    jsend = response.get_json()
    assert jsend["status"] == "success", jsend
    assert jsend["data"]["state"] == "failed"

    # Delete the recording.
    response = client.delete(recording_url)
    jsend = response.get_json()
    assert jsend["status"] == "success", jsend

    # Confirm it's gone.
    response = client.get(recording_url)
    jsend = response.get_json()
    assert jsend["status"] == "error"
