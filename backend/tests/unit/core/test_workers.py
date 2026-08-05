# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for the worker persistence layer."""

import pytest

import spectre_server.core.recordings as recordings
import spectre_server.core.workers as workers


@pytest.fixture
def db_path(tmp_path) -> str:
    """A fresh, initialised SQLite DB file per test."""
    path = str(tmp_path / "recordings.db")
    recordings.init_db(path)
    return path


def _insert_recording(db_path: str, tag: str = "tag-a") -> recordings.Recording:
    return recordings.insert(
        kind="signal",
        tag=tag,
        duration_seconds=1.0,
        db_path=db_path,
    )


def test_insert_worker_returns_row(db_path: str) -> None:
    rec = _insert_recording(db_path)
    worker = workers.insert(rec.id, 4242, db_path=db_path)
    assert worker.recording_id == rec.id
    assert worker.pid == 4242
    assert worker.id > 0


def test_insert_worker_rejects_unknown_recording(db_path: str) -> None:
    with pytest.raises(recordings.RecordingNotFound):
        workers.insert("deadbeef", 1, db_path=db_path)


def test_list_by_recording_returns_insertion_order(db_path: str) -> None:
    rec = _insert_recording(db_path)
    w1 = workers.insert(rec.id, 100, db_path=db_path)
    w2 = workers.insert(rec.id, 200, db_path=db_path)
    w3 = workers.insert(rec.id, 300, db_path=db_path)
    rows = workers.list_by_recording(rec.id, db_path=db_path)
    assert [w.id for w in rows] == [w1.id, w2.id, w3.id]
    assert [w.pid for w in rows] == [100, 200, 300]


def test_list_by_recording_isolates_recordings(db_path: str) -> None:
    a = _insert_recording(db_path, tag="a")
    b = _insert_recording(db_path, tag="b")
    workers.insert(a.id, 1, db_path=db_path)
    workers.insert(b.id, 2, db_path=db_path)
    a_rows = workers.list_by_recording(a.id, db_path=db_path)
    b_rows = workers.list_by_recording(b.id, db_path=db_path)
    assert [w.pid for w in a_rows] == [1]
    assert [w.pid for w in b_rows] == [2]


def test_get_returns_none_for_unknown_worker(db_path: str) -> None:
    rec = _insert_recording(db_path)
    assert workers.get(rec.id, 9999, db_path=db_path) is None


def test_get_returns_worker(db_path: str) -> None:
    rec = _insert_recording(db_path)
    inserted = workers.insert(rec.id, 555, db_path=db_path)
    fetched = workers.get(rec.id, inserted.id, db_path=db_path)
    assert fetched is not None
    assert fetched.pid == 555


def test_get_scoped_by_recording(db_path: str) -> None:
    a = _insert_recording(db_path, tag="a")
    b = _insert_recording(db_path, tag="b")
    inserted = workers.insert(a.id, 42, db_path=db_path)
    # Same worker id under the wrong recording resolves to None.
    assert workers.get(b.id, inserted.id, db_path=db_path) is None


def test_delete_recording_cascades_workers(db_path: str) -> None:
    rec = _insert_recording(db_path)
    workers.insert(rec.id, 1, db_path=db_path)
    workers.insert(rec.id, 2, db_path=db_path)
    recordings.delete(rec.id, db_path=db_path)
    assert workers.list_by_recording(rec.id, db_path=db_path) == []
