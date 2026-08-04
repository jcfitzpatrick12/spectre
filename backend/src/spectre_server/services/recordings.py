# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""Recording lifecycle service layer.

Owns the transition from HTTP request semantics to persistence + process
supervision. Route handlers should call these functions and translate the
returned ids / dicts into URLs and JSend payloads; they should not touch
the recording DB or spawn subprocesses directly.

Multi-tag requests are fanned out: each tag becomes its own recording row
with its own supervisor. If any tag conflicts, we roll back the rows we
already inserted for the batch (no supervisor was spawned for them yet).

Anything that goes wrong — bad input, unknown id, tag conflict, missing
config — is signalled by raising an exception. The route-layer JSend
wrapper converts every uncaught exception into a JSend ``error`` response,
so callers get a traceback and a 500. No JsendFail plumbing here.
"""

import dataclasses  # noqa: F401 (retained for future explicit projections)
import logging
import os
import signal as signal_module
import subprocess
import sys
import time
import typing

import spectre_server.core.logs
import spectre_server.core.receivers
import spectre_server.core.recordings

_LOGGER = logging.getLogger(__name__)

# Polling cadence used by the BC endpoints. 0.5s is long enough to keep DB
# traffic tiny (2 reads/sec) and short enough that a short-duration recording
# still returns promptly.
_POLL_INTERVAL = 0.5

_VALID_STATE_FILTERS = frozenset(
    s.value for s in spectre_server.core.recordings.RecordingState
)
_VALID_KINDS = frozenset({"signal", "spectrogram"})
_REQUESTABLE_STATE = "stopped"


# Explicit wire-projection of a `Recording`. Listed by hand rather than
# derived from `dataclasses.asdict` so a new DB column can't silently leak
# onto the wire; the reverse case (a wire field that isn't in the row) is
# caught by the AttributeError this raises.
_WIRE_FIELDS: tuple[str, ...] = (
    "id",
    "kind",
    "tag",
    "duration_seconds",
    "created_at",
    "started_at",
    "terminal_at",
    "stop_requested_at",
)


def _recording_to_dict(
    recording: spectre_server.core.recordings.Recording,
) -> dict[str, typing.Any]:
    """Serialise a `Recording` for JSON responses.

    Uses an explicit field list rather than ``dataclasses.asdict`` so that
    adding a new column to the row does not automatically publish it, and
    so ``supervisor_pid`` cannot leak.
    """
    payload: dict[str, typing.Any] = {
        field: getattr(recording, field) for field in _WIRE_FIELDS
    }
    payload["state"] = recording.state.value
    return payload


def _validate_configs_exist(tags: list[str]) -> None:
    """Fail-fast: refuse to spawn a supervisor for missing configs."""
    missing: list[str] = []
    for tag in tags:
        try:
            spectre_server.core.receivers.read_config(tag)
        except FileNotFoundError:
            missing.append(tag)
    if missing:
        raise FileNotFoundError(f"No configs found for tags: {missing}.")


def _spawn_supervisor(
    recording_id: str,
    force_restart: bool,
    max_restarts: int,
    skip_validation: bool,
) -> subprocess.Popen:
    """Launch a supervisor subprocess for the given recording.

    Runtime knobs travel as CLI flags rather than being persisted in the row.
    Inherits the parent environment so the subprocess sees the same
    `SPECTRE_DATA_DIR_PATH` (and hence the same DB and configs directory) as
    the backend. `start_new_session=True` detaches the child from the backend
    worker's process group so gunicorn's worker recycling can't inadvertently
    kill in-flight recordings.
    """
    argv = [
        sys.executable,
        "-m",
        "spectre_server.supervisor",
        "--recording-id",
        recording_id,
        "--max-restarts",
        str(max_restarts),
    ]
    if force_restart:
        argv.append("--force-restart")
    if skip_validation:
        argv.append("--skip-validation")
    return subprocess.Popen(
        argv,
        env=os.environ.copy(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def _sigterm_supervisor(pid: typing.Optional[int]) -> None:
    """Best-effort SIGTERM. No-op if pid is unset or the process is gone."""
    if pid is None:
        return
    try:
        os.kill(pid, signal_module.SIGTERM)
    except ProcessLookupError:
        _LOGGER.info("Supervisor pid %s already gone; no signal needed.", pid)


@spectre_server.core.logs.log_call
def create_recording(
    kind: str,
    tags: list[str],
    duration: float,
    force_restart: bool = False,
    max_restarts: int = 5,
    validate: bool = True,
) -> list[str]:
    """Create one recording per tag and spawn each supervisor.

    Returns the created recording ids in ``tags`` order; the route layer
    turns those into resource URLs. On tag conflict for any tag in the
    batch, previously-inserted rows in the batch are deleted and the whole
    batch fails; no supervisor was spawned for those rows.
    """
    if kind not in _VALID_KINDS:
        raise ValueError(
            f"Invalid kind {kind!r}; must be one of: {sorted(_VALID_KINDS)}."
        )
    if not tags:
        raise ValueError("At least one tag is required.")
    if duration is None or float(duration) <= 0:
        raise ValueError("Duration must be a positive number of seconds.")

    _validate_configs_exist(tags)

    inserted: list[spectre_server.core.recordings.Recording] = []
    try:
        for tag in tags:
            inserted.append(
                spectre_server.core.recordings.insert(
                    kind=kind,
                    tag=tag,
                    duration_seconds=float(duration),
                )
            )
    except spectre_server.core.recordings.RecordingConflict:
        for prior in inserted:
            spectre_server.core.recordings.delete(prior.id)
        raise

    for recording in inserted:
        _spawn_supervisor(
            recording.id,
            force_restart=bool(force_restart),
            max_restarts=int(max_restarts),
            skip_validation=not bool(validate),
        )
    return [r.id for r in inserted]


@spectre_server.core.logs.log_call
def list_recordings(
    state: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
    kind: typing.Optional[str] = None,
) -> list[str]:
    """Return recording ids matching the filters, in creation order.

    Unknown ``state`` or ``kind`` values are rejected. ``tag`` is a free-form
    string filter (an unknown tag simply returns an empty list).
    """
    if state is not None and state not in _VALID_STATE_FILTERS:
        raise ValueError(
            f"Invalid state {state!r}; must be one of: {sorted(_VALID_STATE_FILTERS)}."
        )
    if kind is not None and kind not in _VALID_KINDS:
        raise ValueError(
            f"Invalid kind {kind!r}; must be one of: {sorted(_VALID_KINDS)}."
        )
    return spectre_server.core.recordings.list_ids(state=state, tag=tag, kind=kind)


@spectre_server.core.logs.log_call
def get_recording(id: str) -> dict[str, typing.Any]:
    """Return a single recording as a dict.

    Raises ``RecordingNotFound`` if ``id`` is unknown.
    """
    recording = spectre_server.core.recordings.get(id)
    if recording is None:
        raise spectre_server.core.recordings.RecordingNotFound(id)
    return _recording_to_dict(recording)


@spectre_server.core.logs.log_call
def request_state(id: str, state: str) -> str:
    """Request a state transition for a recording.

    Currently only ``stopped`` is a legal request; other states are set by
    the system itself. Idempotent: if the recording is already in a terminal
    state, this is a no-op and returns the id.
    """
    if state != _REQUESTABLE_STATE:
        raise ValueError(
            f"Cannot request state {state!r}; only {_REQUESTABLE_STATE!r} may "
            f"be requested."
        )

    recording = spectre_server.core.recordings.get(id)
    if recording is None:
        raise spectre_server.core.recordings.RecordingNotFound(id)
    if recording.state in spectre_server.core.recordings.TERMINAL_STATES:
        return id

    spectre_server.core.recordings.set_stop_requested_at(id)
    _sigterm_supervisor(recording.supervisor_pid)
    return id


@spectre_server.core.logs.log_call
def delete_recording(id: str) -> str:
    """Remove a terminal recording. Refuses pending / running rows.

    Deleting a live recording would orphan the supervisor and leak DB state;
    clients must stop first, then delete. Returns the id that was deleted.
    """
    recording = spectre_server.core.recordings.get(id)
    if recording is None:
        raise spectre_server.core.recordings.RecordingNotFound(id)
    if recording.state not in spectre_server.core.recordings.TERMINAL_STATES:
        raise RuntimeError(
            f"Cannot delete recording {id!r} in state "
            f"{recording.state.value!r}; request stop first."
        )
    spectre_server.core.recordings.delete(id)
    return id


def _wait_for_terminal_state(
    id: str,
) -> spectre_server.core.recordings.Recording:
    """Block until the recording reaches a terminal state, polling the DB."""
    while True:
        recording = spectre_server.core.recordings.get(id)
        if recording is None:
            raise RuntimeError(f"Recording {id!r} disappeared during poll.")
        if recording.state in spectre_server.core.recordings.TERMINAL_STATES:
            return recording
        time.sleep(_POLL_INTERVAL)


def _bc_record(
    kind: str,
    tags: list[str],
    duration: float,
    force_restart: bool,
    max_restarts: int,
    validate: bool,
) -> int:
    """Shared implementation for the BC ``signal`` / ``spectrograms`` helpers.

    Creates one recording per tag, spawns their supervisors, polls until every
    row is terminal, and returns ``0`` iff all completed. Any non-completed
    terminal state raises ``RuntimeError`` so the JSend layer converts it into
    an ``error`` response — preserving the old semantics where a mid-recording
    failure surfaced as HTTP 500.
    """
    ids = create_recording(
        kind, tags, duration, force_restart, max_restarts, validate
    )
    outcomes = [_wait_for_terminal_state(rid) for rid in ids]
    non_completed = [
        r for r in outcomes
        if r.state is not spectre_server.core.recordings.RecordingState.COMPLETED
    ]
    if non_completed:
        summary = ", ".join(
            f"{r.id}={r.state.value}" for r in non_completed
        )
        raise RuntimeError(f"Recordings finished non-completed: {summary}.")
    return 0


@spectre_server.core.logs.log_call
def signal(
    tags: list[str],
    duration: float,
    force_restart: bool = False,
    max_restarts: int = 5,
    validate: bool = True,
) -> int:
    """Backwards-compatible synchronous ``signal`` recording.

    Blocks the HTTP request until the recording terminates. Kept for
    compatibility with clients that predate ``POST /recordings``.
    """
    return _bc_record(
        "signal", tags, duration, force_restart, max_restarts, validate
    )


@spectre_server.core.logs.log_call
def spectrograms(
    tags: list[str],
    duration: float,
    force_restart: bool = False,
    max_restarts: int = 5,
    validate: bool = True,
) -> int:
    """Backwards-compatible synchronous ``spectrogram`` recording.

    Blocks the HTTP request until the recording terminates. Kept for
    compatibility with clients that predate ``POST /recordings``.
    """
    return _bc_record(
        "spectrogram", tags, duration, force_restart, max_restarts, validate
    )
