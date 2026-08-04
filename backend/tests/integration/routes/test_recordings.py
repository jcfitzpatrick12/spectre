# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""End-to-end tests for the recording HTTP surface.

The tests exercise route + service + core + supervisor together against a
temporary data directory. `SPECTRE_DATA_DIR_PATH` is monkey-patched into
`os.environ` before the Flask app is built so both the backend process and
the supervisor subprocess see the same DB and configs directory.

All error paths are surfaced as JSend ``error`` responses (there is no
``JsendFail`` plumbing in this module): the tests assert on ``status`` and
spot-check the ``message`` string.
"""

import time
import typing
import urllib.parse

import flask
import flask.testing
import pytest

import spectre_server.core.config
import spectre_server.core.receivers
import spectre_server.core.recordings
from spectre_server.__main__ import make_app


COSINE_WAVE_PARAMETERS = {
    "batch_size": 1,
    "amplitude": 3.0,
    "frequency": 16000.0,
    "window_hop": 256,
    "window_size": 256,
    "window_type": "boxcar",
    "sample_rate": 128000,
}


@pytest.fixture
def spectre_data_dir(
    tmp_path, monkeypatch
) -> typing.Iterator[str]:
    """Point `SPECTRE_DATA_DIR_PATH` at a fresh tmp directory for the test."""
    data_dir = tmp_path / "spectre-data"
    data_dir.mkdir()
    monkeypatch.setenv("SPECTRE_DATA_DIR_PATH", str(data_dir))
    spectre_server.core.config.paths.set_spectre_data_dir_path(str(data_dir))
    yield str(data_dir)


@pytest.fixture
def app(spectre_data_dir: str) -> typing.Iterator[flask.Flask]:
    app = make_app()
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture
def client(app: flask.Flask) -> flask.testing.FlaskClient:
    return app.test_client()


def _write_cosine_wave_config(tag: str) -> None:
    receiver = spectre_server.core.receivers.get_receiver(
        "signal_generator", "cosine_wave"
    )
    receiver.write_config(tag, COSINE_WAVE_PARAMETERS)


def _id_from_url(url: str) -> str:
    """Extract the trailing recording id from a resource URL."""
    return urllib.parse.urlparse(url).path.rstrip("/").rsplit("/", 1)[-1]


def _wait_for_state(
    client: flask.testing.FlaskClient,
    id: str,
    state: str,
    timeout: float = 15.0,
) -> dict[str, typing.Any]:
    deadline = time.time() + timeout
    last: typing.Optional[dict[str, typing.Any]] = None
    while time.time() < deadline:
        response = client.get(f"/recordings/{id}")
        payload = response.get_json()
        if payload["status"] == "success" and payload["data"]["state"] == state:
            return payload["data"]
        last = payload
        time.sleep(0.05)
    raise AssertionError(
        f"Recording never reached {state}; last payload = {last!r}"
    )


def test_create_recording_returns_urls(
    client: flask.testing.FlaskClient,
) -> None:
    _write_cosine_wave_config("create-and-wait")
    response = client.post(
        "/recordings",
        json={"kind": "signal", "tags": ["create-and-wait"], "duration": 1.5},
    )
    payload = response.get_json()
    assert payload["status"] == "success"
    urls = payload["data"]
    assert isinstance(urls, list) and len(urls) == 1
    id = _id_from_url(urls[0])
    completed = _wait_for_state(client, id, "completed", timeout=30.0)
    assert completed["tag"] == "create-and-wait"
    assert completed["kind"] == "signal"
    assert completed["started_at"] is not None
    assert completed["terminal_at"] is not None
    # `supervisor_pid` is a server-side detail and must not leak on the wire.
    assert "supervisor_pid" not in completed


def test_create_recording_rejects_missing_kind(
    client: flask.testing.FlaskClient,
) -> None:
    response = client.post(
        "/recordings",
        json={"tags": ["x"], "duration": 1.0},
    )
    payload = response.get_json()
    assert payload["status"] == "error"
    assert "kind" in payload["message"].lower()


def test_create_recording_rejects_unknown_tag(
    client: flask.testing.FlaskClient,
) -> None:
    response = client.post(
        "/recordings",
        json={"kind": "signal", "tags": ["nonexistent"], "duration": 1.0},
    )
    payload = response.get_json()
    assert payload["status"] == "error"
    assert "nonexistent" in payload["message"]


def test_create_recording_rejects_bad_duration(
    client: flask.testing.FlaskClient,
) -> None:
    _write_cosine_wave_config("bad-duration")
    response = client.post(
        "/recordings",
        json={"kind": "signal", "tags": ["bad-duration"], "duration": 0},
    )
    payload = response.get_json()
    assert payload["status"] == "error"
    assert "duration" in payload["message"].lower()


def test_create_recording_conflict_on_duplicate_tag(
    client: flask.testing.FlaskClient,
) -> None:
    _write_cosine_wave_config("conflict-tag")
    first = client.post(
        "/recordings",
        json={"kind": "signal", "tags": ["conflict-tag"], "duration": 30.0},
    )
    assert first.get_json()["status"] == "success"
    first_id = _id_from_url(first.get_json()["data"][0])
    try:
        second = client.post(
            "/recordings",
            json={"kind": "signal", "tags": ["conflict-tag"], "duration": 5.0},
        )
        payload = second.get_json()
        assert payload["status"] == "error"
        assert "RecordingConflict" in payload["message"]
    finally:
        client.patch(f"/recordings/{first_id}", json={"state": "stopped"})
        _wait_for_state(client, first_id, "stopped", timeout=15.0)


def test_list_recordings_filters(client: flask.testing.FlaskClient) -> None:
    _write_cosine_wave_config("list-a")
    _write_cosine_wave_config("list-b")

    a_urls = client.post(
        "/recordings",
        json={"kind": "signal", "tags": ["list-a"], "duration": 1.5},
    ).get_json()["data"]
    b_urls = client.post(
        "/recordings",
        json={"kind": "signal", "tags": ["list-b"], "duration": 1.5},
    ).get_json()["data"]
    a_id = _id_from_url(a_urls[0])
    b_id = _id_from_url(b_urls[0])

    all_response = client.get("/recordings").get_json()
    assert all_response["status"] == "success"
    ids = {_id_from_url(u) for u in all_response["data"]}
    assert {a_id, b_id} <= ids

    filtered = client.get("/recordings?tag=list-a").get_json()
    filtered_ids = [_id_from_url(u) for u in filtered["data"]]
    assert filtered_ids == [a_id]

    _wait_for_state(client, a_id, "completed", timeout=30.0)
    _wait_for_state(client, b_id, "completed", timeout=30.0)


def test_list_recordings_rejects_invalid_state(
    client: flask.testing.FlaskClient,
) -> None:
    response = client.get("/recordings?state=bogus")
    payload = response.get_json()
    assert payload["status"] == "error"
    assert "state" in payload["message"].lower()


def test_list_recordings_rejects_invalid_kind(
    client: flask.testing.FlaskClient,
) -> None:
    response = client.get("/recordings?kind=bogus")
    payload = response.get_json()
    assert payload["status"] == "error"
    assert "kind" in payload["message"].lower()


def test_get_recording_unknown_id_returns_error(
    client: flask.testing.FlaskClient,
) -> None:
    response = client.get("/recordings/deadbeef")
    payload = response.get_json()
    assert payload["status"] == "error"
    assert "RecordingNotFound" in payload["message"]


def test_patch_stops_running_recording(
    client: flask.testing.FlaskClient,
) -> None:
    _write_cosine_wave_config("stop-me")
    urls = client.post(
        "/recordings",
        json={"kind": "signal", "tags": ["stop-me"], "duration": 60.0},
    ).get_json()["data"]
    id = _id_from_url(urls[0])
    _wait_for_state(client, id, "running", timeout=15.0)

    response = client.patch(f"/recordings/{id}", json={"state": "stopped"})
    payload = response.get_json()
    assert payload["status"] == "success"
    assert _id_from_url(payload["data"]) == id

    stopped = _wait_for_state(client, id, "stopped", timeout=15.0)
    assert stopped["stop_requested_at"] is not None
    assert stopped["terminal_at"] is not None


def test_patch_rejects_missing_state(
    client: flask.testing.FlaskClient,
) -> None:
    _write_cosine_wave_config("patch-body")
    urls = client.post(
        "/recordings",
        json={"kind": "signal", "tags": ["patch-body"], "duration": 60.0},
    ).get_json()["data"]
    id = _id_from_url(urls[0])
    try:
        response = client.patch(f"/recordings/{id}", json={})
        payload = response.get_json()
        assert payload["status"] == "error"
    finally:
        client.patch(f"/recordings/{id}", json={"state": "stopped"})
        _wait_for_state(client, id, "stopped", timeout=15.0)


def test_patch_rejects_non_stopped_state(
    client: flask.testing.FlaskClient,
) -> None:
    _write_cosine_wave_config("patch-bad-state")
    urls = client.post(
        "/recordings",
        json={"kind": "signal", "tags": ["patch-bad-state"], "duration": 60.0},
    ).get_json()["data"]
    id = _id_from_url(urls[0])
    try:
        response = client.patch(f"/recordings/{id}", json={"state": "running"})
        payload = response.get_json()
        assert payload["status"] == "error"
        assert "stopped" in payload["message"]
    finally:
        client.patch(f"/recordings/{id}", json={"state": "stopped"})
        _wait_for_state(client, id, "stopped", timeout=15.0)


def test_delete_refuses_live_recording(
    client: flask.testing.FlaskClient,
) -> None:
    _write_cosine_wave_config("no-delete-live")
    urls = client.post(
        "/recordings",
        json={"kind": "signal", "tags": ["no-delete-live"], "duration": 60.0},
    ).get_json()["data"]
    id = _id_from_url(urls[0])
    try:
        response = client.delete(f"/recordings/{id}")
        payload = response.get_json()
        assert payload["status"] == "error"
        assert "stop first" in payload["message"]
    finally:
        client.patch(f"/recordings/{id}", json={"state": "stopped"})
        _wait_for_state(client, id, "stopped", timeout=15.0)


def test_delete_removes_terminal_recording(
    client: flask.testing.FlaskClient,
) -> None:
    _write_cosine_wave_config("delete-me")
    urls = client.post(
        "/recordings",
        json={"kind": "signal", "tags": ["delete-me"], "duration": 1.5},
    ).get_json()["data"]
    id = _id_from_url(urls[0])
    _wait_for_state(client, id, "completed", timeout=30.0)

    response = client.delete(f"/recordings/{id}")
    payload = response.get_json()
    assert payload["status"] == "success"
    assert _id_from_url(payload["data"]) == id

    follow_up = client.get(f"/recordings/{id}")
    assert follow_up.get_json()["status"] == "error"


def test_bc_signal_endpoint_still_works(
    client: flask.testing.FlaskClient,
) -> None:
    _write_cosine_wave_config("bc-signal")
    response = client.post(
        "/recordings/signal",
        json={"tags": ["bc-signal"], "duration": 1.5},
    )
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["data"] == 0

    urls = client.get("/recordings?tag=bc-signal").get_json()["data"]
    assert len(urls) == 1


def test_bc_spectrogram_endpoint_still_works(
    client: flask.testing.FlaskClient,
) -> None:
    _write_cosine_wave_config("bc-spec")
    response = client.post(
        "/recordings/spectrogram",
        json={"tags": ["bc-spec"], "duration": 1.5},
    )
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["data"] == 0
