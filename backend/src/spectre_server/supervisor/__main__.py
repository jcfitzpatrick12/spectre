# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""Entry-point for the recording supervisor.

Usage:
    python -m spectre_server.supervisor --recording-id <id>
        [--force-restart] [--max-restarts N] [--skip-validation]

The supervisor exits with 0 for every legitimate terminal state (including
``failed`` and ``stopped``); a non-zero exit code indicates that the
supervisor itself crashed and the row could not be reconciled — the backend
boot-time reconciliation will then mark the row ``failed``.

Runtime knobs (``--force-restart``, ``--max-restarts``, ``--skip-validation``)
are passed on the command line by the service layer rather than persisted in
the recording row, because they are not needed after the run ends.
"""

import argparse
import logging
import os
import signal
import sys
import types
import typing

import spectre_server.core.jobs
import spectre_server.core.logs
import spectre_server.core.receivers
import spectre_server.core.recordings
import spectre_server.core.workers

_LOGGER = logging.getLogger(__name__)

_now = spectre_server.core.recordings.now_iso_z


def _build_workers(
    recording: spectre_server.core.recordings.Recording,
    skip_validation: bool,
) -> list[spectre_server.core.jobs.Worker]:
    """Build the workers for a recording.

    - ``signal`` recordings run one flowgraph worker.
    - ``spectrogram`` recordings additionally run one post-processing worker,
      listed first so it is up and consuming batches before the flowgraph
      starts producing them.

    Each worker registers its PID against the recording on every start
    (including restarts) so the log file it wrote can be located later.
    """
    recording_id = recording.id

    def _register(pid: int) -> None:
        spectre_server.core.workers.insert(recording_id, pid)

    config = spectre_server.core.receivers.read_config(recording.tag)
    flowgraph_worker = spectre_server.core.receivers.make_flowgraph_worker(
        config, skip_validation, on_start=_register
    )
    if recording.kind == "signal":
        return [flowgraph_worker]
    if recording.kind == "spectrogram":
        post_processing_worker = (
            spectre_server.core.receivers.make_post_processing_worker(
                config, skip_validation, on_start=_register
            )
        )
        return [post_processing_worker, flowgraph_worker]
    raise RuntimeError(f"Unknown recording kind: {recording.kind!r}")


def _install_sigterm_handler(job: spectre_server.core.jobs.Job) -> None:
    """Wire SIGTERM to the job's graceful-stop signal.

    Must be installed *after* the ``Job`` is constructed and *before*
    ``job.start()`` returns control to the monitor loop, so that a SIGTERM
    arriving mid-monitor causes the loop to exit at its next tick rather than
    raising ``KeyboardInterrupt``.
    """

    def _handler(
        signum: int, frame: typing.Optional[types.FrameType]
    ) -> None:
        _LOGGER.info("SIGTERM received; requesting job stop.")
        job.request_stop()

    signal.signal(signal.SIGTERM, _handler)


def _decide_terminal_state(
    recording_id: str,
    monitor_error: typing.Optional[BaseException],
) -> spectre_server.core.recordings.RecordingState:
    """Terminal state decision.

    Order matters. A user-requested stop always wins over ``failed``: if a
    RuntimeError happened at the same time as the stop request, we prefer
    ``stopped`` because that reflects the user's intent and matches what
    ``request_stop`` promised (graceful, non-erroring termination).
    """
    fresh = spectre_server.core.recordings.get(recording_id)
    if fresh is not None and fresh.stop_requested_at is not None:
        return spectre_server.core.recordings.RecordingState.STOPPED
    if isinstance(monitor_error, RuntimeError):
        return spectre_server.core.recordings.RecordingState.FAILED
    return spectre_server.core.recordings.RecordingState.COMPLETED


def _run(
    recording_id: str,
    force_restart: bool,
    max_restarts: int,
    skip_validation: bool,
) -> int:
    spectre_server.core.logs.configure_root_logger(
        spectre_server.core.logs.ProcessType.WORKER,
    )
    _LOGGER.info(
        "Supervisor started for recording %s (pid=%d).",
        recording_id,
        os.getpid(),
    )

    recording = spectre_server.core.recordings.get(recording_id)
    if recording is None:
        _LOGGER.error("Recording %s not found; aborting.", recording_id)
        return 1

    spectre_server.core.recordings.set_supervisor_pid(recording_id, os.getpid())

    # Fast-path: a stop was requested before the supervisor got scheduled. Go
    # straight to `stopped` without ever building workers.
    if recording.stop_requested_at is not None:
        _LOGGER.info(
            "Stop requested before start; short-circuiting to stopped."
        )
        spectre_server.core.recordings.set_state(
            recording_id,
            spectre_server.core.recordings.RecordingState.STOPPED,
            finished_at=_now(),
        )
        return 0

    monitor_error: typing.Optional[BaseException] = None
    try:
        workers = _build_workers(recording, skip_validation)
        job = spectre_server.core.jobs.Job(workers)
        _install_sigterm_handler(job)
        job.start()
        spectre_server.core.recordings.set_state(
            recording_id,
            spectre_server.core.recordings.RecordingState.RUNNING,
            started_at=_now(),
        )
        try:
            job.monitor(
                duration=recording.duration_seconds,
                force_restart=force_restart,
                max_restarts=max_restarts,
            )
        except RuntimeError as exc:
            monitor_error = exc
            _LOGGER.exception("Worker monitor failed.")
    except Exception as exc:  # noqa: BLE001 — we log and translate to `failed`.
        monitor_error = exc
        _LOGGER.exception("Supervisor failed before workers reached steady state.")

    terminal_state = _decide_terminal_state(recording_id, monitor_error)
    # Handle the corner case: exception raised while state is still `pending`
    # because we blew up before `set_state(RUNNING)`. Legal transitions from
    # `pending` are `running`, `stopped`, `failed` — so `stopped` and
    # `failed` are safe here; `completed` is not (nor should the supervisor
    # ever be reporting `completed` from `pending`).
    try:
        spectre_server.core.recordings.set_state(
            recording_id,
            terminal_state,
            finished_at=_now(),
        )
    except RuntimeError:
        _LOGGER.exception(
            "Illegal terminal transition to %s; forcing to failed.",
            terminal_state.value,
        )
        spectre_server.core.recordings.set_state(
            recording_id,
            spectre_server.core.recordings.RecordingState.FAILED,
            finished_at=_now(),
        )
    _LOGGER.info(
        "Supervisor for recording %s exiting with state=%s.",
        recording_id,
        terminal_state.value,
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="spectre_server.supervisor")
    parser.add_argument("--recording-id", required=True)
    parser.add_argument("--force-restart", action="store_true")
    parser.add_argument("--max-restarts", type=int, default=5)
    parser.add_argument("--skip-validation", action="store_true")
    args = parser.parse_args()
    return _run(
        args.recording_id,
        args.force_restart,
        args.max_restarts,
        args.skip_validation,
    )


if __name__ == "__main__":
    sys.exit(main())
