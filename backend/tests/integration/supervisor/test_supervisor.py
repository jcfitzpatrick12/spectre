# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""End-to-end supervisor tests.

These tests spawn the supervisor as a real subprocess against a temporary
data directory, so they exercise argparse, logging, the SIGTERM handler and
the state-transition machinery together. The signal-generator receiver is
used as a stand-in for a real SDR so no hardware is required.
"""

import os
import signal
import subprocess
import sys
import time
import typing

import pytest

import spectre_server.core.config
import spectre_server.core.receivers
import spectre_server.core.recordings


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
def spectre_env(tmp_path) -> typing.Iterator[dict[str, str]]:
    """A fresh SPECTRE_DATA_DIR_PATH plus initialised recordings DB."""
    data_dir = tmp_path / "spectre-data"
    data_dir.mkdir()
    # Instantiate a Paths so the directory tree gets provisioned.
    spectre_server.core.config.Paths({"SPECTRE_DATA_DIR_PATH": str(data_dir)})
    db_path = str(data_dir / "recordings.db")
    spectre_server.core.recordings.init_db(db_path)
    env = os.environ.copy()
    env["SPECTRE_DATA_DIR_PATH"] = str(data_dir)
    yield env


def _write_cosine_wave_config(
    tag: str, spectre_data_dir_path: str
) -> None:
    """Write a signal-generator cosine-wave config into the given data dir."""
    paths = spectre_server.core.config.Paths(
        {"SPECTRE_DATA_DIR_PATH": spectre_data_dir_path}
    )
    receiver = spectre_server.core.receivers.get_receiver(
        "signal_generator", "cosine_wave"
    )
    receiver.write_config(
        tag,
        COSINE_WAVE_PARAMETERS,
        configs_dir_path=paths.get_configs_dir_path(),
    )


def _spawn_supervisor(
    recording_id: str, env: dict[str, str]
) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, "-m", "spectre_server.supervisor", "--recording-id", recording_id],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _wait_for_state(
    recording_id: str,
    state: spectre_server.core.recordings.RecordingState,
    db_path: str,
    timeout: float = 10.0,
) -> spectre_server.core.recordings.Recording:
    deadline = time.time() + timeout
    while time.time() < deadline:
        rec = spectre_server.core.recordings.get(recording_id, db_path=db_path)
        if rec is not None and rec.state is state:
            return rec
        time.sleep(0.05)
    rec = spectre_server.core.recordings.get(recording_id, db_path=db_path)
    raise AssertionError(
        f"Recording never reached {state.value}; last state = "
        f"{rec.state.value if rec else 'MISSING'}"
    )


def test_supervisor_short_circuits_on_pre_requested_stop(spectre_env) -> None:
    data_dir = spectre_env["SPECTRE_DATA_DIR_PATH"]
    db_path = os.path.join(data_dir, "recordings.db")

    _write_cosine_wave_config("shortcircuit", data_dir)
    rec = spectre_server.core.recordings.insert(
        kind="signal",
        tag="shortcircuit",
        duration_seconds=60.0,
        db_path=db_path,
    )
    spectre_server.core.recordings.set_stop_requested_at(rec.id, db_path=db_path)

    proc = _spawn_supervisor(rec.id, spectre_env)
    proc.wait(timeout=15)
    assert proc.returncode == 0

    fetched = spectre_server.core.recordings.get(rec.id, db_path=db_path)
    assert fetched is not None
    assert fetched.state is spectre_server.core.recordings.RecordingState.STOPPED
    # We short-circuited: no workers were ever built, no started_at.
    assert fetched.started_at is None
    assert fetched.finished_at is not None


def test_supervisor_completes_signal_recording(spectre_env) -> None:
    data_dir = spectre_env["SPECTRE_DATA_DIR_PATH"]
    db_path = os.path.join(data_dir, "recordings.db")

    _write_cosine_wave_config("complete", data_dir)
    rec = spectre_server.core.recordings.insert(
        kind="signal",
        tag="complete",
        duration_seconds=2.0,
        db_path=db_path,
    )

    proc = _spawn_supervisor(rec.id, spectre_env)
    proc.wait(timeout=30)
    assert proc.returncode == 0, proc.stderr.read().decode()

    fetched = spectre_server.core.recordings.get(rec.id, db_path=db_path)
    assert fetched is not None
    assert fetched.state is spectre_server.core.recordings.RecordingState.COMPLETED
    assert fetched.started_at is not None
    assert fetched.finished_at is not None
    assert fetched.supervisor_pid == proc.pid


def test_supervisor_stops_mid_recording_on_sigterm(spectre_env) -> None:
    data_dir = spectre_env["SPECTRE_DATA_DIR_PATH"]
    db_path = os.path.join(data_dir, "recordings.db")

    _write_cosine_wave_config("stop-mid", data_dir)
    rec = spectre_server.core.recordings.insert(
        kind="signal",
        tag="stop-mid",
        duration_seconds=60.0,
        db_path=db_path,
    )

    proc = _spawn_supervisor(rec.id, spectre_env)
    try:
        # Wait until the supervisor has transitioned the row to RUNNING; only
        # after that point does SIGTERM produce a legitimate `stopped` outcome.
        _wait_for_state(
            rec.id,
            spectre_server.core.recordings.RecordingState.RUNNING,
            db_path,
            timeout=15,
        )
        spectre_server.core.recordings.set_stop_requested_at(rec.id, db_path=db_path)
        os.kill(proc.pid, signal.SIGTERM)
        proc.wait(timeout=15)
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)

    assert proc.returncode == 0

    fetched = spectre_server.core.recordings.get(rec.id, db_path=db_path)
    assert fetched is not None
    assert fetched.state is spectre_server.core.recordings.RecordingState.STOPPED
    assert fetched.started_at is not None
    assert fetched.stop_requested_at is not None
    assert fetched.finished_at is not None
