# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""Persistence for worker rows.

Each row is the minimum information needed to locate the log file a worker
wrote. The supervisor is the sole writer; workers themselves never touch
the DB.
"""

import dataclasses
import typing

from . import recordings as _recordings


@dataclasses.dataclass
class WorkerRecord:
    """A single worker's persistence row."""

    id: int
    recording_id: str
    pid: int


class WorkerNotFound(Exception):
    """Raised when an operation targets a worker id that does not exist
    under the given recording."""

    def __init__(self, recording_id: str, worker_id: int) -> None:
        super().__init__(
            f"Worker {worker_id!r} not found for recording {recording_id!r}"
        )
        self.recording_id = recording_id
        self.worker_id = worker_id


def _row_to_worker(row: typing.Any) -> WorkerRecord:
    return WorkerRecord(
        id=row["id"],
        recording_id=row["recording_id"],
        pid=row["pid"],
    )


def insert(
    recording_id: str,
    pid: int,
    db_path: typing.Optional[str] = None,
) -> WorkerRecord:
    """Record a running worker under a recording.

    :raises RecordingNotFound: if the recording does not exist.
    """
    with _recordings._txn(db_path) as conn:
        _recordings._require_exists(conn, recording_id)
        cursor = conn.execute(
            "INSERT INTO worker (recording_id, pid) VALUES (?, ?)",
            (recording_id, pid),
        )
        worker_id = cursor.lastrowid
    return WorkerRecord(id=int(worker_id), recording_id=recording_id, pid=pid)


def list_by_recording(
    recording_id: str,
    db_path: typing.Optional[str] = None,
) -> list[WorkerRecord]:
    """List worker rows for a recording, ordered by insertion."""
    conn = _recordings._connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM worker WHERE recording_id = ? ORDER BY id",
            (recording_id,),
        ).fetchall()
        return [_row_to_worker(r) for r in rows]
    finally:
        conn.close()


def get(
    recording_id: str,
    worker_id: int,
    db_path: typing.Optional[str] = None,
) -> typing.Optional[WorkerRecord]:
    """Return the worker row, or ``None`` if unknown under this recording."""
    conn = _recordings._connect(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM worker WHERE recording_id = ? AND id = ?",
            (recording_id, worker_id),
        ).fetchone()
        if row is None:
            return None
        return _row_to_worker(row)
    finally:
        conn.close()
