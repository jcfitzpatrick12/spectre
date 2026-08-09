# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import datetime
from time import sleep

import spectre_server.core.config
import spectre_server.core.jobs


def _short_sleep() -> None:
    sleep(spectre_server.core.jobs.Duration.ONE_CENTISECOND)


def _dt(hour: int, minute: int, second: int = 0) -> datetime.datetime:
    return datetime.datetime(2025, 1, 31, hour, minute, second)


def _sleep_forever() -> None:
    """Sleep indefinetely."""
    while True:
        _short_sleep()


def _fail_instantly() -> None:
    raise RuntimeError("Boom!")


def _make_successful_runtime_worker() -> spectre_server.core.jobs.Worker:
    return spectre_server.core.jobs.make_worker(
        "successful_runtime_worker", _sleep_forever
    )


def _make_instantly_failing_runtime_worker() -> spectre_server.core.jobs.Worker:
    return spectre_server.core.jobs.make_worker(
        "instantly_failing_runtime_worker", _fail_instantly
    )


@pytest.fixture
def successful_runtime_worker() -> spectre_server.core.jobs.Worker:
    """A worker which models successful runtime.

    The created `Worker` instance manages a process which sleeps indefinitely.
    """
    return _make_successful_runtime_worker()


@pytest.fixture
def instantly_failing_runtime_worker() -> spectre_server.core.jobs.Worker:
    """A worker which models runtime that fails instantly.

    The created `Worker` instance manages a process which instantly fails.
    """
    return _make_instantly_failing_runtime_worker()


@pytest.fixture
def successful_runtime_job() -> spectre_server.core.jobs.Job:
    """Create a job modelling successful runtime.

    Return a `Job` instance,  where each worker sleeps indefinitely.
    """
    _num_workers = 2  # arbitrarily choose two workers
    workers = [_make_successful_runtime_worker() for _ in range(_num_workers)]
    return spectre_server.core.jobs.Job(workers)


@pytest.fixture
def partially_failing_job() -> spectre_server.core.jobs.Job:
    """Create a job modelling partially failing runtime.

    Return a `Job` instance, where one worker sleeps indefinitely, and one fails instantly.
    """
    workers = [
        _make_instantly_failing_runtime_worker(),
        _make_successful_runtime_worker(),
    ]
    return spectre_server.core.jobs.Job(workers)


@pytest.fixture
def recording_manager(
    spectre_config_paths: spectre_server.core.config.Paths,
) -> spectre_server.core.jobs.RecordingManager:
    return spectre_server.core.jobs.RecordingManager(spectre_config_paths.get_db_path())


@pytest.fixture
def new_recording() -> spectre_server.core.jobs.RecordingRecord:
    return spectre_server.core.jobs.RecordingRecord(
        "123",
        "foo",
        spectre_server.core.jobs.RecordingKind.SIGNAL,
        spectre_server.core.jobs.RecordingState.RUNNING,
        120.0,
        False,
        _dt(0, 0, 0),
        finished_at=None,
    )


@pytest.fixture
def new_worker(
    new_recording: spectre_server.core.jobs.RecordingRecord,
) -> spectre_server.core.jobs.WorkerRecord:
    return spectre_server.core.jobs.WorkerRecord(
        spectre_server.core.jobs.WorkerName.SIGNAL, new_recording.id
    )


class TestWorker:
    def test_name(
        self, successful_runtime_worker: spectre_server.core.jobs.Worker
    ) -> None:
        """Check that the name of the process is as expected."""
        assert successful_runtime_worker.name == "successful_runtime_worker"

    def test_is_alive(
        self, successful_runtime_worker: spectre_server.core.jobs.Worker
    ) -> None:
        """Check that a worker which is successfully running is alive."""
        successful_runtime_worker.start()
        _short_sleep()
        assert successful_runtime_worker.is_alive

        # Kill the process, since otherwise they would keep running until the parent process terminates.
        successful_runtime_worker.kill()

    def test_is_not_alive(
        self, instantly_failing_runtime_worker: spectre_server.core.jobs.Worker
    ) -> None:
        """Check that a worker which instantly failed, is not alive."""
        instantly_failing_runtime_worker.start()
        _short_sleep()
        assert not instantly_failing_runtime_worker.is_alive

    def test_kill(
        self, successful_runtime_worker: spectre_server.core.jobs.Worker
    ) -> None:
        """Check that killing the worker, results in it not being alive."""
        successful_runtime_worker.start()
        successful_runtime_worker.kill()
        _short_sleep()
        assert not successful_runtime_worker.is_alive

    def test_restart(
        self, successful_runtime_worker: spectre_server.core.jobs.Worker
    ) -> None:
        """Check that a restarted worker evaluates as alive."""
        successful_runtime_worker.start()
        successful_runtime_worker.restart()
        _short_sleep()
        assert successful_runtime_worker.is_alive

        # Kill the process, since otherwise they would keep running until the parent process terminates.
        successful_runtime_worker.kill()

    def test_multiple_restarts(
        self, successful_runtime_worker: spectre_server.core.jobs.Worker
    ) -> None:
        """Check that a worker can be restarted multiple times."""
        successful_runtime_worker.start()
        successful_runtime_worker.restart()
        successful_runtime_worker.restart()

        _short_sleep()

        assert successful_runtime_worker.is_alive

        # Kill the process, since otherwise they would keep running until the parent process terminates.
        successful_runtime_worker.kill()

    def test_starting_twice(
        self, successful_runtime_worker: spectre_server.core.jobs.Worker
    ) -> None:
        """Check that a worker cannot be started twice."""
        with pytest.raises(RuntimeError):
            successful_runtime_worker.start()
            successful_runtime_worker.start()

        # Kill the process, since otherwise they would keep running until the parent process terminates.
        successful_runtime_worker.kill()

    def test_killing_dead_process(
        self, successful_runtime_worker: spectre_server.core.jobs.Worker
    ) -> None:
        """Check that we cannot kill a process which is not alive."""
        with pytest.raises(RuntimeError):
            successful_runtime_worker.kill()


class TestJobs:

    def test_start(self, successful_runtime_job: spectre_server.core.jobs.Job) -> None:
        """Check that when a job starts, the workers are all alive."""
        successful_runtime_job.start()
        _short_sleep()
        assert successful_runtime_job.workers_are_alive

        # Kill the workers, since otherwise they would keep running until the parent process terminates.
        successful_runtime_job.kill()

    def test_kill(self, successful_runtime_job: spectre_server.core.jobs.Job) -> None:
        """Check that when a job is started, then killed, that the workers are not alive."""
        successful_runtime_job.start()
        successful_runtime_job.kill()
        _short_sleep()

        # Check all the workers are not alive.
        assert not successful_runtime_job.workers_are_alive

    def test_monitor_successful_job(
        self, successful_runtime_job: spectre_server.core.jobs.Job
    ) -> None:
        """Check that once the total runtime of a job is complete, the workers are no longer alive."""
        successful_runtime_job.start()
        successful_runtime_job.monitor(
            spectre_server.core.jobs.Duration.ONE_CENTISECOND
        )

        # Sleep for a moment, to give the job time to kill the workers once the total runtime has elapsed.
        _short_sleep()

        # Check all the workers are not alive.
        assert not successful_runtime_job.workers_are_alive

    def test_monitor_failed_job(
        self, partially_failing_job: spectre_server.core.jobs.Job
    ) -> None:
        """Check that if a worker fails, and force restart is false, that the main process raises a `RuntimeError`."""
        partially_failing_job.start()
        with pytest.raises(RuntimeError):
            partially_failing_job.monitor(spectre_server.core.jobs.Duration.ONE_SECOND)

        # Check all the workers are not alive.
        assert not partially_failing_job.workers_are_alive

    def test_max_restarts(
        self, partially_failing_job: spectre_server.core.jobs.Job
    ) -> None:
        """Check that we don't get any neverending force restart loops."""
        partially_failing_job.start()
        _max_restarts = 3
        with pytest.raises(
            RuntimeError,
            match=f"Maximum number of restarts has been reached: {_max_restarts}",
        ):
            partially_failing_job.monitor(
                spectre_server.core.jobs.Duration.TEN_SECONDS,
                force_restart=True,
                max_restarts=_max_restarts,
            )

        # Check all the workers are not alive.
        assert not partially_failing_job.workers_are_alive

    def test_single_restart(
        self, successful_runtime_job: spectre_server.core.jobs.Job
    ) -> None:
        """Check that we can restart a job multiple once, and the workers are alive afterwards."""
        successful_runtime_job.start()
        successful_runtime_job.restart()
        _short_sleep()
        assert successful_runtime_job.workers_are_alive

        # Kill the workers, since otherwise they would keep running until the parent process terminates.
        successful_runtime_job.kill()

    def test_multiple_restarts(
        self, successful_runtime_job: spectre_server.core.jobs.Job
    ) -> None:
        """Check that we can restart a job multiple times, and that the workers are alive afterwards."""
        successful_runtime_job.start()
        successful_runtime_job.restart()
        successful_runtime_job.restart()
        _short_sleep()
        assert successful_runtime_job.workers_are_alive

        # Kill the workers, since otherwise they would keep running until the parent process terminates.
        successful_runtime_job.kill()

    def test_starting_twice(
        self, successful_runtime_job: spectre_server.core.jobs.Job
    ) -> None:
        """Check that we cannot start a job twice."""
        with pytest.raises(RuntimeError):
            successful_runtime_job.start()
            successful_runtime_job.start()

        # Kill the workers, since otherwise they would keep running until the parent process terminates.
        successful_runtime_job.kill()

    def test_should_stop_immediate(
        self, successful_runtime_job: spectre_server.core.jobs.Job
    ) -> None:
        """A should_stop callable that returns True immediately should exit without error."""
        successful_runtime_job.start()
        successful_runtime_job.monitor(
            spectre_server.core.jobs.Duration.TEN_SECONDS,
            should_stop=lambda: True,
        )
        _short_sleep()
        assert not successful_runtime_job.workers_are_alive

    def test_should_stop_after_n_ticks(
        self, successful_runtime_job: spectre_server.core.jobs.Job
    ) -> None:
        """A should_stop callable that trips after three ticks should exit without error."""
        tick_count = 0

        def stop_after_three() -> bool:
            nonlocal tick_count
            tick_count += 1
            return tick_count >= 3

        successful_runtime_job.start()
        successful_runtime_job.monitor(
            spectre_server.core.jobs.Duration.TEN_SECONDS,
            should_stop=stop_after_three,
        )
        _short_sleep()
        assert not successful_runtime_job.workers_are_alive
        assert tick_count >= 3


class TestRecordingManager:

    def test_instantiation(
        self, spectre_config_paths: spectre_server.core.config.Paths
    ) -> None:
        """Creating a `RecordingManager` instance should create an empty database."""
        recording_manager = spectre_server.core.jobs.RecordingManager(
            spectre_config_paths.get_db_path()
        )
        assert recording_manager.get("missing") is None
        assert recording_manager.get_ids() == []
        assert recording_manager.get_workers("missing") == []

    def test_repeated_instantiation(
        self, spectre_config_paths: spectre_server.core.config.Paths
    ) -> None:
        """Repeated initialization should leave the database usable and empty."""
        db_path = spectre_config_paths.get_db_path()
        first = spectre_server.core.jobs.RecordingManager(db_path)
        second = spectre_server.core.jobs.RecordingManager(db_path)
        assert first.get_ids() == []
        assert second.get_ids() == []

    def test_get_recording_unknown_id(
        self,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """Fetching an unknown recording should return nothing."""
        assert recording_manager.get("missing") is None

    def test_register_new_returns_overridden_id(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """Callers may override the generated recording identifier."""
        id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=new_recording.id,
        )
        assert id == new_recording.id

    def test_new_recording_round_trip(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """Creating a recording should persist it with a running state."""
        id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=new_recording.id,
        )
        stored = recording_manager.get(id)
        assert (
            stored is not None
            and stored.state == spectre_server.core.jobs.RecordingState.RUNNING
        )
        assert stored == new_recording

    def test_new_recording_with_conflict(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """Two in-flight recordings may not share a tag."""
        recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=new_recording.id,
        )

        with pytest.raises(ValueError, match="already in flight"):
            recording_manager.register_new(
                new_recording.kind,
                new_recording.tag,
                new_recording.duration,
                new_recording.started_at,
                id=new_recording.id,
            )

    def test_new_recording_same_tag_after_finished_state(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """A finished recording should not block a later recording with the same tag."""
        id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=new_recording.id,
        )
        recording_manager.set_completed(id, _dt(0, 1, 0))

        second_id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=None,
        )

        stored = recording_manager.get(second_id)
        assert stored is not None
        assert stored.state is spectre_server.core.jobs.RecordingState.RUNNING

    def test_set_completed_round_trip(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """A running recording should transition to completed."""
        id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=new_recording.id,
        )
        recording_manager.set_completed(id, _dt(0, 1, 0))

        completed_recording = recording_manager.get(id)
        assert completed_recording is not None
        assert completed_recording.id == new_recording.id
        assert completed_recording.tag == new_recording.tag
        assert completed_recording.kind == new_recording.kind
        assert (
            completed_recording.state
            == spectre_server.core.jobs.RecordingState.COMPLETED
        )
        assert completed_recording.duration == new_recording.duration
        assert completed_recording.started_at == new_recording.started_at
        assert completed_recording.finished_at == _dt(0, 1, 0)

    def test_set_failed_round_trip(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """A running recording should transition to failed."""
        id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=new_recording.id,
        )
        recording_manager.set_failed(id, _dt(0, 1, 0))

        failed_recording = recording_manager.get(id)
        assert failed_recording is not None
        assert failed_recording.id == new_recording.id
        assert failed_recording.tag == new_recording.tag
        assert failed_recording.kind == new_recording.kind
        assert failed_recording.state == spectre_server.core.jobs.RecordingState.FAILED
        assert failed_recording.duration == new_recording.duration
        assert failed_recording.started_at == new_recording.started_at
        assert failed_recording.finished_at == _dt(0, 1, 0)

    def test_set_failed_on_missing_recording(
        self, recording_manager: spectre_server.core.jobs.RecordingManager
    ) -> None:
        """Check that setting a non-existent recording to failed raises."""
        with pytest.raises(ValueError, match="does not exist"):
            recording_manager.set_failed("missing", _dt(0, 0, 0))

    def test_set_completed_on_missing_recording(
        self, recording_manager: spectre_server.core.jobs.RecordingManager
    ) -> None:
        """Check that setting a non-existent recording to completed raises."""
        with pytest.raises(ValueError, match="does not exist"):
            recording_manager.set_completed("missing", _dt(0, 0, 0))

    def test_completed_to_completed_is_illegal(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """A completed recording may not transition again."""
        id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=new_recording.id,
        )
        recording_manager.set_completed(id, _dt(0, 1, 0))

        with pytest.raises(ValueError, match="Illegal recording state transition"):
            recording_manager.set_completed(id, _dt(0, 1, 0))

    def test_failed_to_failed_is_illegal(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """A failed recording may not transition again."""
        id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=new_recording.id,
        )
        recording_manager.set_failed(id, _dt(0, 1, 0))

        with pytest.raises(ValueError, match="Illegal recording state transition"):
            recording_manager.set_failed(id, _dt(0, 1, 0))

    def test_get_ids_no_recording_manager(
        self, recording_manager: spectre_server.core.jobs.RecordingManager
    ) -> None:
        """Getting recording ids where none exist should return an empty list."""
        assert recording_manager.get_ids() == []

    def test_get_ids_no_filter(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """All recording ids should be returned when no filter is provided."""
        id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=None,
        )
        assert recording_manager.get_ids() == [id]

    def test_get_ids_state_filter(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """Filtering ids by state should return only matching recording_manager."""
        first_id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=None,
        )
        recording_manager.set_completed(first_id, _dt(0, 1, 0))

        second_id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=None,
        )
        recording_manager.set_failed(second_id, _dt(0, 2, 0))

        third_id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=None,
        )

        assert recording_manager.get_ids() == [first_id, second_id, third_id]
        assert recording_manager.get_ids(
            state=spectre_server.core.jobs.RecordingState.COMPLETED
        ) == [first_id]
        assert recording_manager.get_ids(
            state=spectre_server.core.jobs.RecordingState.FAILED
        ) == [second_id]
        assert recording_manager.get_ids(
            state=spectre_server.core.jobs.RecordingState.RUNNING
        ) == [third_id]

    def test_delete_nothing(
        self, recording_manager: spectre_server.core.jobs.RecordingManager
    ) -> None:
        """Deleting an unknown recording should raise"""
        with pytest.raises(ValueError, match="does not exist"):
            recording_manager.delete("missing")

    def test_delete_existing_recording(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """Deleting an existing recording should remove it."""
        id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=None,
        )
        recording_manager.delete(id)
        assert recording_manager.get(id) is None
        assert recording_manager.get_ids() == []

    def test_delete_recording_cascades_to_workers(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        new_worker: spectre_server.core.jobs.WorkerRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """Deleting a recording should remove its registered workers."""
        id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=new_recording.id,
        )
        recording_manager.register_workers(
            id, [spectre_server.core.jobs.WorkerName.SIGNAL]
        )
        assert recording_manager.get_workers(id) == [new_worker]
        assert recording_manager.get(id) == new_recording

        recording_manager.delete(id)

        assert recording_manager.get(id) is None
        assert recording_manager.get_workers(id) == []

    def test_mark_in_flight_failed(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """Backend startup should mark stale running recordings as failed."""
        first_id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=None,
        )
        recording_manager.set_completed(first_id, _dt(0, 1, 0))

        second_id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=None,
        )
        recording_manager.set_failed(second_id, _dt(0, 2, 0))

        third_id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=None,
        )

        recording_manager.mark_in_flight_failed(_dt(0, 2, 0))

        first_recording = recording_manager.get(first_id)
        second_recording = recording_manager.get(second_id)
        third_recording = recording_manager.get(third_id)
        assert first_recording is not None
        assert second_recording is not None
        assert third_recording is not None
        assert (
            first_recording.state == spectre_server.core.jobs.RecordingState.COMPLETED
        )
        assert second_recording.state == spectre_server.core.jobs.RecordingState.FAILED
        assert third_recording.state == spectre_server.core.jobs.RecordingState.FAILED

    def test_register_workers_round_trip(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        new_worker: spectre_server.core.jobs.WorkerRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """Registered workers should be persisted and retrievable."""
        id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            new_recording.id,
        )
        recording_manager.register_workers(id, [new_worker.name])
        worker = recording_manager.get_worker(id, new_worker.name)
        assert worker == new_worker

    def test_register_workers_unknown_recording_raises(
        self,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """Registering workers under an unknown recording should fail explicitly."""
        with pytest.raises(ValueError, match="does not exist"):
            recording_manager.register_workers(
                "missing", [spectre_server.core.jobs.WorkerName.SIGNAL]
            )

    def test_get_worker_unknown_worker_returns_none(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """Looking up an unknown worker under an existing recording should return nothing."""
        id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            new_recording.id,
        )
        assert (
            recording_manager.get_worker(id, spectre_server.core.jobs.WorkerName.SIGNAL)
            is None
        )

    def test_get_worker_unknown_recording_returns_none(
        self,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """Looking up a worker under an unknown recording should return nothing."""
        assert (
            recording_manager.get_worker(
                "missing", spectre_server.core.jobs.WorkerName.SIGNAL
            )
            is None
        )

    def test_get_workers_when_empty(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """A recording with no workers should return an empty worker-id list."""
        id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            new_recording.id,
        )
        assert recording_manager.get_workers(id) == []

    def test_get_worker_ids_unknown_recording_returns_empty(
        self,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """Looking up worker ids for an unknown recording should return an empty list."""
        assert recording_manager.get_workers("missing") == []

    def test_request_stop(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """Check that requesting stop does so."""
        id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=None,
        )
        stored = recording_manager.get(id)
        # No stop is requested at initialisation.
        assert stored is not None and not stored.stop_requested
        assert not recording_manager.stop_requested(id)

        recording_manager.request_stop(id)
        stored = recording_manager.get(id)
        assert stored is not None and stored.stop_requested
        assert recording_manager.stop_requested(id)

    def test_request_stop_is_idempotent(
        self,
        new_recording: spectre_server.core.jobs.RecordingRecord,
        recording_manager: spectre_server.core.jobs.RecordingManager,
    ) -> None:
        """Check that requesting stop has the same effect on repeat requests."""
        id = recording_manager.register_new(
            new_recording.kind,
            new_recording.tag,
            new_recording.duration,
            new_recording.started_at,
            id=None,
        )
        stored = recording_manager.get(id)
        assert stored is not None and not stored.stop_requested
        assert not recording_manager.stop_requested(id)

        for _ in range(3):
            recording_manager.request_stop(id)
            stored = recording_manager.get(id)
            assert stored is not None and stored.stop_requested
            assert recording_manager.stop_requested(id)
