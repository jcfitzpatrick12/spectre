# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import typing
import threading

import spectre_server.core.config
import spectre_server.core.jobs
import spectre_server.core.logs
import spectre_server.core.receivers

_LOGGER = logging.getLogger(__name__)


def _resolve_paths(
    paths: typing.Optional[spectre_server.core.config.Paths],
) -> spectre_server.core.config.Paths:
    return paths if paths is not None else spectre_server.core.config.paths


def _make_workers(
    kind: spectre_server.core.jobs.RecordingKind,
    tag: str,
    recording_id: str,
    validate: bool,
    paths: typing.Optional[spectre_server.core.config.Paths] = None,
) -> list[spectre_server.core.jobs.Worker]:
    configs_dir_path = paths.get_configs_dir_path() if paths is not None else None
    logs_dir_path = (
        paths.get_logs_dir_path(spectre_server.core.logs.ProcessType.WORKER.value)
        if paths is not None
        else None
    )
    spectre_data_dir_path = (
        paths.get_spectre_data_dir_path() if paths is not None else None
    )
    config = spectre_server.core.receivers.read_config(
        tag, configs_dir_path=configs_dir_path
    )
    skip_validation = not validate

    workers = [
        spectre_server.core.receivers.make_signal_worker(
            config,
            recording_id,
            skip_validation,
            logs_dir_path=logs_dir_path,
            spectre_data_dir_path=spectre_data_dir_path,
        ),
    ]
    if kind is spectre_server.core.jobs.RecordingKind.SPECTROGRAM:
        workers.append(
            spectre_server.core.receivers.make_spectrograms_worker(
                config,
                recording_id,
                skip_validation,
                logs_dir_path=logs_dir_path,
                spectre_data_dir_path=spectre_data_dir_path,
            )
        )
    return workers


def _start_job(
    recording_id: str,
    kind: spectre_server.core.jobs.RecordingKind,
    tag: str,
    duration: float,
    force_restart: bool,
    max_restarts: int,
    validate: bool,
    paths: typing.Optional[spectre_server.core.config.Paths] = None,
) -> None:
    recording_manager = spectre_server.core.jobs.RecordingManager(
        _resolve_paths(paths).get_db_path()
    )

    try:
        workers = _make_workers(kind, tag, recording_id, validate, paths)
        recording_manager.register_workers(
            recording_id,
            [spectre_server.core.jobs.WorkerName(worker.name) for worker in workers],
        )
        job = spectre_server.core.jobs.Job(workers)
        job.start()
        job.monitor(
            duration,
            force_restart=force_restart,
            max_restarts=max_restarts,
            should_stop=lambda: recording_manager.stop_requested(recording_id),
        )
        recording_manager.set_completed(
            recording_id, spectre_server.core.config.utc_now()
        )
    except Exception:
        _LOGGER.exception("Recording '%s' failed", recording_id)
        recording_manager.set_failed(recording_id, spectre_server.core.config.utc_now())


@spectre_server.core.logs.log_call
def create_recording(
    tag: str,
    kind: str,
    duration: float,
    force_restart: bool = False,
    max_restarts: int = 5,
    validate: bool = True,
    paths: typing.Optional[spectre_server.core.config.Paths] = None,
) -> str:
    """Create a recording and run it asynchronously in a local background thread.

    :ivar tag: The tag of the config used for the recording.
    :ivar kind: Recording kind.
    :ivar duration: Requested recording duration in seconds.
    :param force_restart: If specified, restart all workers if one dies unexpectedly.
    :param max_restarts: Maximum number of times workers can be restarted before giving up and killing all workers.
    Only applies when force_restart is True. Defaults to 5.
    :param validate: If True, validate the config parameters. Defaults to True.
    :param paths: Optionally override the directory used to store data at runtime.
    :returns: The recording identifier.
    """
    recording_kind = spectre_server.core.jobs.RecordingKind(kind)
    recording_manager = spectre_server.core.jobs.RecordingManager(
        _resolve_paths(paths).get_db_path()
    )
    recording_id = recording_manager.register_new(
        recording_kind,
        tag,
        duration,
        spectre_server.core.config.utc_now(),
    )

    thread = threading.Thread(
        target=_start_job,
        args=(
            recording_id,
            recording_kind,
            tag,
            duration,
            force_restart,
            max_restarts,
            validate,
            paths,
        ),
        name=f"recording-{recording_id}",
        daemon=True,
    )
    thread.start()
    return recording_id


def _open_recording_manager(
    db_path: typing.Optional[str],
) -> spectre_server.core.jobs.RecordingManager:
    return spectre_server.core.jobs.RecordingManager(
        db_path
        if db_path is not None
        else spectre_server.core.config.paths.get_db_path()
    )


@spectre_server.core.logs.log_call
def get_recording(
    id: str,
    db_path: typing.Optional[str] = None,
) -> dict[str, typing.Any]:
    """Get recording metadata.

    :param id: The recording identifier.
    :param db_path: Optionally override the db used at runtime.
    :returns: Metadata about the recording.
    """
    recording_manager = _open_recording_manager(db_path)
    recording = recording_manager.get(id)
    if recording is None:
        raise KeyError(f"Recording '{id}' does not exist")

    started_at = recording.started_at.strftime(
        spectre_server.core.config.TimeFormat.DATETIME
    )
    finished_at = (
        recording.finished_at.strftime(spectre_server.core.config.TimeFormat.DATETIME)
        if recording.finished_at is not None
        else None
    )
    return {
        "id": recording.id,
        "tag": recording.tag,
        "kind": recording.kind.value,
        "state": recording.state.value,
        "duration": recording.duration,
        "stop_requested": recording.stop_requested,
        "started_at": started_at,
        "finished_at": finished_at,
    }


@spectre_server.core.logs.log_call
def get_recordings(
    states: list[spectre_server.core.jobs.RecordingState],
    db_path: typing.Optional[str] = None,
) -> list[str]:
    """Get ids of recordings.

    :param states: Look for recordings of these states. If none are provided, look for recordings with any state.
    :param db_path: Optionally override the db used at runtime.
    """
    recording_manager = _open_recording_manager(db_path)
    if not states:
        return recording_manager.get_ids()
    ids: list[str] = []
    for state in states:
        ids += recording_manager.get_ids(state=state)
    return ids


@spectre_server.core.logs.log_call
def delete_recording(
    id: str,
    db_path: typing.Optional[str] = None,
) -> str:
    """Request a stop and immediately remove the recording record.

    :param id: The recording identifier.
    :param db_path: Optionally override the db used at runtime.
    :returns: The identifier of the (deleted) recording.
    """
    recording_manager = _open_recording_manager(db_path)
    recording_manager.request_stop(id)
    recording_manager.delete(id)
    return id


@spectre_server.core.logs.log_call
def stop_recording(
    recording_id: str,
    db_path: typing.Optional[str] = None,
) -> str:
    """Request a recording to stop.

    :param recording_id: The recording identifier.
    :param db_path: Optionally override the db used at runtime.
    :returns: The recording identifier.
    """
    recording_manager = _open_recording_manager(db_path)
    recording_manager.request_stop(recording_id)
    return recording_id


@spectre_server.core.logs.log_call
def get_workers(
    id: str,
    db_path: typing.Optional[str] = None,
) -> list[str]:
    """Get the names of workers under a recording.

    :param id: The recording identifier.
    :param db_path: Optionally override the db used at runtime.
    :returns: A list of worker names.
    """
    recording_manager = _open_recording_manager(db_path)
    return [w.name.value for w in recording_manager.get_workers(id)]


def _resolve_worker_name(worker_name: str) -> spectre_server.core.jobs.WorkerName:
    try:
        return spectre_server.core.jobs.WorkerName(worker_name)
    except ValueError as exc:
        raise KeyError(f"Unknown worker name '{worker_name}'") from exc


@spectre_server.core.logs.log_call
def get_worker(
    id: str,
    worker_name: str,
    db_path: typing.Optional[str] = None,
) -> dict[str, typing.Any]:
    """Get metadata for a worker under a recording.

    :param id: The recording identifier.
    :param worker_name: The worker name.
    :param db_path: Optionally override the db used at runtime.
    :returns: Metadata about the worker.
    """
    name = _resolve_worker_name(worker_name)
    recording_manager = _open_recording_manager(db_path)
    worker = recording_manager.get_worker(id, name)
    if worker is None:
        raise KeyError(f"Worker '{worker_name}' does not exist under recording '{id}'")
    return {
        "name": worker.name.value,
        "recording_id": worker.recording_id,
    }


@spectre_server.core.logs.log_call
def get_worker_log(
    id: str,
    worker_name: str,
    db_path: typing.Optional[str] = None,
    logs_dir_path: typing.Optional[str] = None,
) -> str:
    """Read the log file for a worker under a recording.

    :param id: The recording identifier.
    :param worker_name: The worker name.
    :param db_path: Optionally override the db used at runtime.
    :param db_path: Optionally override the directory used to find logs.
    :returns: The contents of the worker log file.
    """
    name = _resolve_worker_name(worker_name)
    recording_manager = _open_recording_manager(db_path)
    worker = recording_manager.get_worker(id, name)
    if worker is None:
        raise KeyError(f"Worker '{worker_name}' does not exist under recording '{id}'")
    file_path = spectre_server.core.logs.get_worker_log_file_path(
        worker.recording_id,
        worker.name.value,
        logs_dir_path=logs_dir_path,
    )
    return spectre_server.core.logs.Log(file_path).read()
