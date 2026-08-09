# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses
import datetime
import enum
import typing
import sqlite3
import contextlib
import secrets

import spectre_server.core.config


class RecordingKind(enum.Enum):
    """What kind of data is being recorded."""

    SIGNAL = "signal"
    SPECTROGRAM = "spectrogram"


class RecordingState(enum.Enum):
    """The lifecycle state of a recording."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


_LEGAL_TRANSITIONS = {
    RecordingState.RUNNING: [
        RecordingState.COMPLETED,
        RecordingState.FAILED,
    ],
    # The recording has ended, its state is immutable.
    RecordingState.COMPLETED: [],
    RecordingState.FAILED: [],
}

_RECORDING_TABLE = "recording"
_WORKER_TABLE = "worker"

_NBYTES_ID = 4


@dataclasses.dataclass
class RecordingRecord:
    """Persisted recording metadata.

    :ivar id: Recording identifier.
    :ivar tag: The tag of the config used for the recording.
    :ivar kind: Recording kind.
    :ivar state: The state of the recording in its lifecycle.
    :ivar duration: Requested recording duration in seconds.
    :ivar stop_requested: If true, the recording was requested to stop.
    :ivar started_at: When the recording started.
    :ivar finished_at: When the recording ended.
    """

    id: str  # PK
    tag: str
    kind: RecordingKind
    state: RecordingState
    duration: float
    stop_requested: bool
    started_at: datetime.datetime
    finished_at: typing.Optional[datetime.datetime] = None


class WorkerName(enum.Enum):
    SIGNAL = "signal"
    SPECTROGRAM = "spectrogram"


@dataclasses.dataclass
class WorkerRecord:
    """Persisted worker metadata.

    :param name: The name of the worker.
    :param recording_id: Parent recording identifier.
    """

    name: WorkerName
    recording_id: str  # FK


class RecordingManager:
    """Persist and book-keep recordings and their underlying workers."""

    def __init__(self, db_path: typing.Optional[str] = None) -> None:
        self.__db_path = db_path or spectre_server.core.config.paths.get_db_path()
        self.__create_tables()

    @contextlib.contextmanager
    def __connect(self) -> typing.Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.__db_path)
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def __create_tables(self) -> None:
        with self.__connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(f"""
            CREATE TABLE IF NOT EXISTS {_RECORDING_TABLE} (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                tag TEXT NOT NULL,
                duration REAL NOT NULL,
                state TEXT NOT NULL,
                stop_requested INTEGER NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS {_WORKER_TABLE} (
                name TEXT,
                recording_id TEXT NOT NULL REFERENCES {_RECORDING_TABLE}(id) ON DELETE CASCADE,
                PRIMARY KEY (name, recording_id)
            );
            """)

    @staticmethod
    def __serialize_datetime(dt_value: datetime.datetime) -> str:
        return dt_value.strftime(spectre_server.core.config.TimeFormat.DATETIME)

    @staticmethod
    def __deserialise_datetime(
        dt_value: str,
    ) -> datetime.datetime:
        return datetime.datetime.strptime(
            dt_value,
            spectre_server.core.config.TimeFormat.DATETIME,
        )

    @staticmethod
    def __row_to_recording(row: sqlite3.Row) -> RecordingRecord:
        return RecordingRecord(
            id=row["id"],
            tag=row["tag"],
            kind=RecordingKind(row["kind"]),
            state=RecordingState(row["state"]),
            duration=row["duration"],
            stop_requested=bool(row["stop_requested"]),
            started_at=RecordingManager.__deserialise_datetime(row["started_at"]),
            finished_at=(
                RecordingManager.__deserialise_datetime(row["finished_at"])
                if row["finished_at"] is not None
                else None
            ),
        )

    @staticmethod
    def __row_to_worker(row: sqlite3.Row) -> WorkerRecord:
        return WorkerRecord(WorkerName(row["name"]), row["recording_id"])

    def get(self, id: str) -> typing.Optional[RecordingRecord]:
        """Get a recording by its identifier.

        :returns: A container if it exists, None if it doesn't.
        """
        with self.__connect() as conn:
            res = conn.execute(f"SELECT * FROM {_RECORDING_TABLE} WHERE id = ?", (id,))
            row = res.fetchone()
            if row is None:
                return None
            return self.__row_to_recording(row)

    def __require(self, id: str) -> RecordingRecord:
        """Return the recording or raise if it does not exist."""
        recording = self.get(id)
        if recording is None:
            raise ValueError(f"Recording '{id}' does not exist.")
        return recording

    def __already_in_flight(
        self,
        tag: str,
        conn: sqlite3.Connection,
    ) -> bool:
        """Two in-flight recordings can't share a tag."""
        res = conn.execute(
            f"SELECT 1 FROM {_RECORDING_TABLE} WHERE tag = ? AND state = ?",
            (tag, RecordingState.RUNNING.value),
        )
        return res.fetchone() is not None

    def register_new(
        self,
        kind: RecordingKind,
        tag: str,
        duration: float,
        started_at: datetime.datetime,
        id: typing.Optional[str] = None,
    ) -> str:
        """Insert a new recording in state `running`.

        :param kind: Recording kind.
        :param tag: The tag of the config used for the recording.
        :param duration: Requested recording duration in seconds.
        :param started_at: When the recording started.
        :param worker_pids: The process ids of workers under the recording.
        :param id: If specified, override the minted recording identifier.
        :return: The identifier for the recording.
        """

        id = id or secrets.token_hex(_NBYTES_ID)
        with self.__connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            if self.__already_in_flight(tag, conn):
                raise ValueError(
                    f"A recording with tag '{tag}' is already in flight. "
                    f"Wait for it to finish, or stop it early."
                )
            conn.execute(
                f"INSERT INTO {_RECORDING_TABLE} (id, kind, tag, duration, state, stop_requested, started_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    id,
                    kind.value,
                    tag,
                    duration,
                    RecordingState.RUNNING.value,
                    False,  # Stop cannot be requeste at registration.
                    self.__serialize_datetime(started_at),
                ),
            )
        return id

    def __set_state(
        self, conn: sqlite3.Connection, id: str, state: RecordingState
    ) -> None:
        res = conn.execute(f"SELECT state FROM {_RECORDING_TABLE} WHERE id = ?", (id,))
        row = res.fetchone()
        if row is None:
            raise ValueError(f"Recording '{id}' does not exist")
        current_state = RecordingState(row["state"])
        if state not in _LEGAL_TRANSITIONS[current_state]:
            raise ValueError(
                f"Illegal recording state transition: "
                f"'{current_state.value}' to '{state.value}' is not allowed"
            )
        conn.execute(
            f"UPDATE {_RECORDING_TABLE} SET state = ? WHERE id = ?",
            (state.value, id),
        )

    def __set_finished(
        self,
        id: str,
        state: RecordingState,
        finished_at: datetime.datetime,
    ) -> None:
        if state not in [
            RecordingState.COMPLETED,
            RecordingState.FAILED,
        ]:
            raise ValueError(f"Expected a finished state. Got {state}")

        self.__require(id)

        with self.__connect() as conn:
            self.__set_state(conn, id, state)
            conn.execute(
                f"UPDATE {_RECORDING_TABLE} SET finished_at = ? WHERE id = ?",
                (
                    self.__serialize_datetime(finished_at),
                    id,
                ),
            )

    def set_completed(self, id: str, finished_at: datetime.datetime) -> None:
        """Transition the state of an in-flight recording to `completed`.

        :param id: The recording identifier.
        """
        self.__set_finished(id, RecordingState.COMPLETED, finished_at)

    def set_failed(self, id: str, finished_at: datetime.datetime) -> None:
        """Transition the state of an in-flight recording to `completed`.

        :param id: The recording identifier.
        """
        self.__set_finished(id, RecordingState.FAILED, finished_at)

    def delete(self, id: str) -> None:
        """Remove a recording. No-op for unknown ids.

        Cascades to any associated worker rows via the FK constraint.

        :param id: The recording identifier.
        """
        self.__require(id)

        with self.__connect() as conn:
            conn.execute(f"DELETE FROM {_RECORDING_TABLE} WHERE id = ?", (id,))

    def get_ids(
        self,
        state: typing.Optional[RecordingState] = None,
    ) -> list[str]:
        """Get ids of all recordings, with optional filtering.

        :param state: Filter recordings with this state.
        """
        with self.__connect() as conn:
            clauses: list[str] = []
            params: list[typing.Any] = []
            if state is not None:
                clauses.append("state = ?")
                params.append(state.value)
            where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
            rows = conn.execute(
                f"SELECT id FROM {_RECORDING_TABLE} {where} ORDER BY started_at",
                params,
            ).fetchall()
            return [r["id"] for r in rows]

    def mark_in_flight_failed(self, finished_at: datetime.datetime) -> None:
        """Only to be called on backend boot.

        Any recording still in flight after a backend restart
        cannot have a live workers, so force their state to failed.

        :param finished_at:
        """
        stale_ids = self.get_ids(state=RecordingState.RUNNING)
        for id in stale_ids:
            self.set_failed(id, finished_at)

    def register_workers(
        self,
        id: str,
        names: list[WorkerName],
    ) -> None:
        """Register workers under a recording.

        :param id: Parent recording identifier.
        :param names: The names of workers to register.
        """
        self.__require(id)

        with self.__connect() as conn:
            for name in names:
                conn.execute(
                    f"""
                    INSERT INTO {_WORKER_TABLE} (name, recording_id) VALUES (?, ?)
                """,
                    (
                        name.value,
                        id,
                    ),
                )

    def get_workers(
        self,
        id: str,
    ) -> list[WorkerRecord]:
        """Get a worker by its identifier.

        :param id: Parent recording identifier.
        :param name: The name of the worker.
        :returns: A list of workers, empty if there's none under the recording.
        """
        with self.__connect() as conn:
            res = conn.execute(
                f"""
                SELECT name, recording_id FROM {_WORKER_TABLE} WHERE recording_id = ?
            """,
                (id,),
            )
            rows = res.fetchall()
            return [self.__row_to_worker(r) for r in rows]

    def get_worker(
        self,
        id: str,
        name: WorkerName,
    ) -> typing.Optional[WorkerRecord]:
        """Get a worker metadata by name.

        :param id: Parent recording identifier.
        :param name: The recording name.
        :returns: A container if it exists, None if it doesn't.
        """
        with self.__connect() as conn:
            res = conn.execute(
                f"""
                SELECT name, recording_id FROM {_WORKER_TABLE} WHERE name = ? AND recording_id = ?
            """,
                (name.value, id),
            )
            row = res.fetchone()
            if row is None:
                return None
            return self.__row_to_worker(row)

    def request_stop(
        self,
        id: str,
    ) -> None:
        """Request a recording to stop.

        :param id: The recording identifier.
        """
        self.__require(id)

        with self.__connect() as conn:
            conn.execute(
                f"UPDATE {_RECORDING_TABLE} SET stop_requested = 1 WHERE id = ?", (id,)
            )

    def stop_requested(
        self,
        id: str,
    ) -> bool:
        """Check whether a stop has been requested."""
        return self.__require(id).stop_requested
