# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for the recordings persistence layer."""

import os

import pytest

import spectre_server.core.recordings as recordings


@pytest.fixture
def db_path(tmp_path) -> str:
    """A fresh, initialised SQLite DB file per test."""
    path = str(tmp_path / "recordings.db")
    recordings.init_db(path)
    return path


def _insert_default(
    db_path: str,
    tag: str = "tag-a",
    kind: str = "signal",
    duration_seconds: float = 5.0,
) -> recordings.Recording:
    return recordings.insert(
        kind=kind,
        tag=tag,
        duration_seconds=duration_seconds,
        db_path=db_path,
    )


def test_init_db_is_idempotent(tmp_path) -> None:
    path = str(tmp_path / "recordings.db")
    recordings.init_db(path)
    recordings.init_db(path)  # must not raise
    assert os.path.exists(path)


def test_insert_returns_pending_recording(db_path: str) -> None:
    rec = _insert_default(db_path, tag="tag-a")
    assert rec.state is recordings.RecordingState.PENDING
    assert rec.kind == "signal"
    assert rec.tag == "tag-a"
    assert len(rec.id) == 16
    assert rec.supervisor_pid is None
    assert rec.started_at is None
    assert rec.terminal_at is None
    assert rec.stop_requested_at is None


def test_insert_rejects_empty_tag(db_path: str) -> None:
    with pytest.raises(ValueError):
        recordings.insert(
            kind="signal",
            tag="",
            duration_seconds=1.0,
            db_path=db_path,
        )


def test_insert_rejects_invalid_kind(db_path: str) -> None:
    with pytest.raises(ValueError):
        recordings.insert(
            kind="bogus",
            tag="tag-a",
            duration_seconds=1.0,
            db_path=db_path,
        )


def test_tag_conflict_raises_for_pending_recording(db_path: str) -> None:
    _insert_default(db_path, tag="tag-a")
    with pytest.raises(recordings.RecordingConflict) as exc_info:
        _insert_default(db_path, tag="tag-a")
    assert exc_info.value.tag == "tag-a"


def test_tag_conflict_raises_for_running_recording(db_path: str) -> None:
    rec = _insert_default(db_path, tag="tag-a")
    recordings.set_state(
        rec.id,
        recordings.RecordingState.RUNNING,
        started_at="2024-01-01T00:00:00+00:00",
        db_path=db_path,
    )
    with pytest.raises(recordings.RecordingConflict):
        _insert_default(db_path, tag="tag-a")


def test_tag_conflict_allowed_after_terminal_state(db_path: str) -> None:
    rec = _insert_default(db_path, tag="tag-a")
    recordings.set_state(
        rec.id,
        recordings.RecordingState.RUNNING,
        started_at="2024-01-01T00:00:00+00:00",
        db_path=db_path,
    )
    recordings.set_state(
        rec.id,
        recordings.RecordingState.COMPLETED,
        terminal_at="2024-01-01T00:00:05+00:00",
        db_path=db_path,
    )
    # No conflict because prior recording is terminal.
    rec2 = _insert_default(db_path, tag="tag-a")
    assert rec2.id != rec.id


def test_get_returns_none_for_unknown_id(db_path: str) -> None:
    assert recordings.get("deadbeef", db_path=db_path) is None


def test_get_round_trips_tag_and_state(db_path: str) -> None:
    rec = _insert_default(db_path, tag="a")
    fetched = recordings.get(rec.id, db_path=db_path)
    assert fetched is not None
    assert fetched.id == rec.id
    assert fetched.tag == "a"
    assert fetched.state is recordings.RecordingState.PENDING


def test_list_ids_filters_by_state_kind_tag(db_path: str) -> None:
    a = _insert_default(db_path, tag="a", kind="signal")
    b = _insert_default(db_path, tag="b", kind="spectrogram")
    c = _insert_default(db_path, tag="c", kind="signal")

    all_ids = recordings.list_ids(db_path=db_path)
    assert set(all_ids) == {a.id, b.id, c.id}

    signal_ids = recordings.list_ids(kind="signal", db_path=db_path)
    assert set(signal_ids) == {a.id, c.id}

    tag_ids = recordings.list_ids(tag="c", db_path=db_path)
    assert tag_ids == [c.id]

    pending_ids = recordings.list_ids(state="pending", db_path=db_path)
    assert set(pending_ids) == {a.id, b.id, c.id}

    running_ids = recordings.list_ids(state="running", db_path=db_path)
    assert running_ids == []


def test_set_state_rejects_illegal_transition(db_path: str) -> None:
    rec = _insert_default(db_path)
    with pytest.raises(RuntimeError):
        # pending -> completed is not legal (must go through running).
        recordings.set_state(
            rec.id,
            recordings.RecordingState.COMPLETED,
            db_path=db_path,
        )


def test_set_state_rejects_transition_from_terminal(db_path: str) -> None:
    rec = _insert_default(db_path)
    recordings.set_state(
        rec.id,
        recordings.RecordingState.FAILED,
        terminal_at="2024-01-01T00:00:00+00:00",
        db_path=db_path,
    )
    with pytest.raises(RuntimeError):
        recordings.set_state(
            rec.id,
            recordings.RecordingState.RUNNING,
            db_path=db_path,
        )


def test_set_state_raises_for_unknown_id(db_path: str) -> None:
    with pytest.raises(recordings.RecordingNotFound):
        recordings.set_state(
            "deadbeef",
            recordings.RecordingState.RUNNING,
            db_path=db_path,
        )


def test_set_supervisor_pid(db_path: str) -> None:
    rec = _insert_default(db_path)
    recordings.set_supervisor_pid(rec.id, 12345, db_path=db_path)
    fetched = recordings.get(rec.id, db_path=db_path)
    assert fetched is not None
    assert fetched.supervisor_pid == 12345


def test_set_supervisor_pid_raises_for_unknown_id(db_path: str) -> None:
    with pytest.raises(recordings.RecordingNotFound):
        recordings.set_supervisor_pid("deadbeef", 1, db_path=db_path)


def test_set_stop_requested_at_is_idempotent(db_path: str) -> None:
    rec = _insert_default(db_path)
    assert recordings.set_stop_requested_at(rec.id, db_path=db_path) is True
    assert recordings.set_stop_requested_at(rec.id, db_path=db_path) is False
    fetched = recordings.get(rec.id, db_path=db_path)
    assert fetched is not None
    assert fetched.stop_requested_at is not None


def test_set_stop_requested_at_raises_for_unknown_id(db_path: str) -> None:
    with pytest.raises(recordings.RecordingNotFound):
        recordings.set_stop_requested_at("deadbeef", db_path=db_path)


def test_delete_removes_recording(db_path: str) -> None:
    rec = _insert_default(db_path, tag="a")
    recordings.delete(rec.id, db_path=db_path)
    assert recordings.get(rec.id, db_path=db_path) is None
    # Tag is free again after delete.
    rec2 = _insert_default(db_path, tag="a")
    assert rec2.id != rec.id


def test_delete_of_unknown_id_is_noop(db_path: str) -> None:
    recordings.delete("deadbeef", db_path=db_path)  # must not raise


def test_mark_stale_as_failed(db_path: str) -> None:
    a = _insert_default(db_path, tag="a")
    b = _insert_default(db_path, tag="b")
    c = _insert_default(db_path, tag="c")

    # b is running, c is already completed.
    recordings.set_state(
        b.id,
        recordings.RecordingState.RUNNING,
        started_at="2024-01-01T00:00:00+00:00",
        db_path=db_path,
    )
    recordings.set_state(
        c.id,
        recordings.RecordingState.RUNNING,
        started_at="2024-01-01T00:00:00+00:00",
        db_path=db_path,
    )
    recordings.set_state(
        c.id,
        recordings.RecordingState.COMPLETED,
        terminal_at="2024-01-01T00:00:05+00:00",
        db_path=db_path,
    )

    reconciled = recordings.mark_stale_as_failed(db_path=db_path)
    assert set(reconciled) == {a.id, b.id}

    fetched_a = recordings.get(a.id, db_path=db_path)
    fetched_b = recordings.get(b.id, db_path=db_path)
    fetched_c = recordings.get(c.id, db_path=db_path)
    assert fetched_a is not None and fetched_a.state is recordings.RecordingState.FAILED
    assert fetched_b is not None and fetched_b.state is recordings.RecordingState.FAILED
    assert fetched_c is not None and fetched_c.state is recordings.RecordingState.COMPLETED
    assert fetched_a.terminal_at is not None
    assert fetched_b.terminal_at is not None
