# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""Persistence layer for recording lifecycle rows.

One recording corresponds to one receiver-configuration tag; multi-tag
requests are handled at the service layer by inserting one row per tag.
Owns the ``recording`` table and its state-machine invariants. Does not
touch OS processes or HTTP. Only fields that are actually read after
insert are persisted here; transient run-time knobs (validation, restart
policy) live on the supervisor's command line.
"""

import contextlib
import dataclasses
import datetime
import enum
import os
import secrets
import sqlite3
import typing

import spectre_server.core.config


class RecordingState(enum.Enum):
    """The lifecycle state of a recording."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    STOPPED = "stopped"
    FAILED = "failed"


TERMINAL_STATES: frozenset[RecordingState] = frozenset(
    {RecordingState.COMPLETED, RecordingState.STOPPED, RecordingState.FAILED}
)


# Which states each state may transition to. Terminal states have no outward
# transitions. `pending` can transition to `failed` directly if the supervisor
# fails before workers start (e.g. missing config).
_LEGAL_TRANSITIONS: dict[RecordingState, frozenset[RecordingState]] = {
    RecordingState.PENDING: frozenset(
        {RecordingState.RUNNING, RecordingState.STOPPED, RecordingState.FAILED}
    ),
    RecordingState.RUNNING: frozenset(
        {RecordingState.COMPLETED, RecordingState.STOPPED, RecordingState.FAILED}
    ),
    RecordingState.COMPLETED: frozenset(),
    RecordingState.STOPPED: frozenset(),
    RecordingState.FAILED: frozenset(),
}


@dataclasses.dataclass
class Recording:
    """A recording lifecycle row.

    One recording is bound to exactly one receiver-configuration ``tag``.
    """

    id: str
    kind: str
    tag: str
    duration_seconds: float
    state: RecordingState
    supervisor_pid: typing.Optional[int]
    created_at: str
    started_at: typing.Optional[str]
    terminal_at: typing.Optional[str]
    stop_requested_at: typing.Optional[str]


class RecordingConflict(Exception):
    """Raised on insert when the requested tag is already claimed by an
    existing non-terminal recording."""

    def __init__(self, tag: str) -> None:
        super().__init__(f"Active recording exists for tag: {tag!r}")
        self.tag = tag


class RecordingNotFound(Exception):
    """Raised when an operation targets an id that does not exist."""

    def __init__(self, id: str) -> None:
        super().__init__(f"Recording not found: {id!r}")
        self.id = id


def _default_db_path() -> str:
    """The default location of the SQLite file, inside the shared data volume."""
    return os.path.join(
        spectre_server.core.config.paths.get_spectre_data_dir_path(),
        "recordings.db",
    )


def now_iso_z() -> str:
    """ISO-8601 UTC timestamp used for all recording timestamps.

    Uses the package-wide :class:`~spectre_server.core.config.TimeFormat`
    ``DATETIME`` format (``%Y-%m-%dT%H:%M:%S.%fZ``) so recording
    timestamps agree with every other timestamp emitted by the backend.
    """
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        spectre_server.core.config.TimeFormat.DATETIME
    )


def _connect(db_path: typing.Optional[str] = None) -> sqlite3.Connection:
    """Open a SQLite connection with WAL mode.

    Uses ``isolation_level=None`` so transactions are managed explicitly with
    ``BEGIN``/``COMMIT``/``ROLLBACK``. This avoids Python's autocommit
    heuristics interfering with our ``BEGIN IMMEDIATE`` writes.
    """
    path = db_path or _default_db_path()
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


@contextlib.contextmanager
def _txn(
    db_path: typing.Optional[str] = None,
) -> typing.Iterator[sqlite3.Connection]:
    """Open a connection, run a ``BEGIN IMMEDIATE`` transaction, and commit on
    clean exit / rollback on exception. Always closes the connection.
    """
    conn = _connect(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        try:
            yield conn
        except BaseException:
            conn.execute("ROLLBACK")
            raise
        else:
            conn.execute("COMMIT")
    finally:
        conn.close()


def _require_exists(conn: sqlite3.Connection, id: str) -> None:
    row = conn.execute(
        "SELECT 1 FROM recording WHERE id = ?", (id,)
    ).fetchone()
    if row is None:
        raise RecordingNotFound(id)


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS recording (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL CHECK (kind IN ('signal', 'spectrogram')),
    tag TEXT NOT NULL,
    duration_seconds REAL NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('pending','running','completed','stopped','failed')),
    supervisor_pid INTEGER,
    created_at TEXT NOT NULL,
    started_at TEXT,
    terminal_at TEXT,
    stop_requested_at TEXT
);

CREATE INDEX IF NOT EXISTS ix_recording_state ON recording(state);
CREATE INDEX IF NOT EXISTS ix_recording_tag ON recording(tag);
"""


def init_db(db_path: typing.Optional[str] = None) -> None:
    """Create the schema if it does not already exist.

    Safe to call on every backend boot; ``CREATE TABLE IF NOT EXISTS`` is a
    no-op when the tables are present.
    """
    conn = _connect(db_path)
    try:
        conn.executescript(_SCHEMA_SQL)
    finally:
        conn.close()


def _row_to_recording(row: sqlite3.Row) -> Recording:
    return Recording(
        id=row["id"],
        kind=row["kind"],
        tag=row["tag"],
        duration_seconds=row["duration_seconds"],
        state=RecordingState(row["state"]),
        supervisor_pid=row["supervisor_pid"],
        created_at=row["created_at"],
        started_at=row["started_at"],
        terminal_at=row["terminal_at"],
        stop_requested_at=row["stop_requested_at"],
    )


def insert(
    kind: str,
    tag: str,
    duration_seconds: float,
    db_path: typing.Optional[str] = None,
) -> Recording:
    """Insert a new recording in state ``pending``.

    Runs inside a ``BEGIN IMMEDIATE`` transaction so the tag-uniqueness check
    and the insert are atomic against any concurrent writer.

    :raises RecordingConflict: if the tag is already claimed by a non-terminal
        (``pending`` or ``running``) recording.
    """
    if kind not in ("signal", "spectrogram"):
        raise ValueError(f"Invalid kind: {kind!r}")
    if not tag:
        raise ValueError("Tag is required.")

    created_at = now_iso_z()
    rec_id = secrets.token_hex(8)
    with _txn(db_path) as conn:
        existing = conn.execute(
            """
            SELECT 1 FROM recording
            WHERE tag = ? AND state IN ('pending', 'running')
            """,
            (tag,),
        ).fetchone()
        if existing is not None:
            raise RecordingConflict(tag)
        conn.execute(
            """
            INSERT INTO recording (
                id, kind, tag, duration_seconds, state, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                rec_id,
                kind,
                tag,
                duration_seconds,
                RecordingState.PENDING.value,
                created_at,
            ),
        )

    return Recording(
        id=rec_id,
        kind=kind,
        tag=tag,
        duration_seconds=duration_seconds,
        state=RecordingState.PENDING,
        supervisor_pid=None,
        created_at=created_at,
        started_at=None,
        terminal_at=None,
        stop_requested_at=None,
    )


def get(
    id: str, db_path: typing.Optional[str] = None
) -> typing.Optional[Recording]:
    """Return the recording with the given id, or None if it does not exist."""
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM recording WHERE id = ?", (id,)
        ).fetchone()
        if row is None:
            return None
        return _row_to_recording(row)
    finally:
        conn.close()


def list_ids(
    state: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
    kind: typing.Optional[str] = None,
    db_path: typing.Optional[str] = None,
) -> list[str]:
    """List recording ids, in creation order. All filters are optional."""
    conn = _connect(db_path)
    try:
        clauses: list[str] = []
        params: list[typing.Any] = []
        if state is not None:
            clauses.append("state = ?")
            params.append(state)
        if kind is not None:
            clauses.append("kind = ?")
            params.append(kind)
        if tag is not None:
            clauses.append("tag = ?")
            params.append(tag)
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        rows = conn.execute(
            f"SELECT id FROM recording {where} ORDER BY created_at",
            params,
        ).fetchall()
        return [r["id"] for r in rows]
    finally:
        conn.close()


def set_supervisor_pid(
    id: str, pid: int, db_path: typing.Optional[str] = None
) -> None:
    """Record the supervisor process's PID on the row."""
    with _txn(db_path) as conn:
        _require_exists(conn, id)
        conn.execute(
            "UPDATE recording SET supervisor_pid = ? WHERE id = ?", (pid, id)
        )


def set_state(
    id: str,
    state: RecordingState,
    started_at: typing.Optional[str] = None,
    terminal_at: typing.Optional[str] = None,
    db_path: typing.Optional[str] = None,
) -> None:
    """Transition the recording to ``state``, enforcing legal transitions.

    :raises RecordingNotFound: if the id does not exist.
    :raises RuntimeError: if the transition from the current state to ``state``
        is not legal (e.g. from a terminal state, or from ``pending`` to
        ``completed``).
    """
    with _txn(db_path) as conn:
        row = conn.execute(
            "SELECT state FROM recording WHERE id = ?", (id,)
        ).fetchone()
        if row is None:
            raise RecordingNotFound(id)
        current = RecordingState(row["state"])
        if state not in _LEGAL_TRANSITIONS[current]:
            raise RuntimeError(
                f"Illegal state transition for recording {id!r}: "
                f"{current.value} -> {state.value}"
            )
        updates = ["state = ?"]
        params: list[typing.Any] = [state.value]
        if started_at is not None:
            updates.append("started_at = ?")
            params.append(started_at)
        if terminal_at is not None:
            updates.append("terminal_at = ?")
            params.append(terminal_at)
        params.append(id)
        conn.execute(
            f"UPDATE recording SET {', '.join(updates)} WHERE id = ?", params
        )


def set_stop_requested_at(
    id: str, db_path: typing.Optional[str] = None
) -> bool:
    """Idempotently mark that a stop has been requested by a client.

    :return: True if this call was the one that set the timestamp; False if it
        was already set (so this call was a no-op).
    :raises RecordingNotFound: if the id does not exist.
    """
    with _txn(db_path) as conn:
        row = conn.execute(
            "SELECT stop_requested_at FROM recording WHERE id = ?", (id,)
        ).fetchone()
        if row is None:
            raise RecordingNotFound(id)
        if row["stop_requested_at"] is not None:
            return False
        conn.execute(
            "UPDATE recording SET stop_requested_at = ? WHERE id = ?",
            (now_iso_z(), id),
        )
        return True


def delete(id: str, db_path: typing.Optional[str] = None) -> None:
    """Remove a recording. No-op if the id is unknown; callers that need to
    detect that case should check with :func:`get` beforehand."""
    conn = _connect(db_path)
    try:
        conn.execute("DELETE FROM recording WHERE id = ?", (id,))
    finally:
        conn.close()


def mark_stale_as_failed(db_path: typing.Optional[str] = None) -> list[str]:
    """Reconciliation step to run on backend boot.

    Any recording still in a non-terminal state after a backend restart cannot
    have a live supervisor (PIDs from prior generations are meaningless), so we
    force-transition it to ``failed``.

    :return: The ids that were reconciled, for logging.
    """
    with _txn(db_path) as conn:
        rows = conn.execute(
            "SELECT id FROM recording WHERE state IN ('pending', 'running')"
        ).fetchall()
        ids = [r["id"] for r in rows]
        if ids:
            conn.execute(
                "UPDATE recording SET state = 'failed', terminal_at = ? "
                "WHERE state IN ('pending', 'running')",
                (now_iso_z(),),
            )
        return ids
