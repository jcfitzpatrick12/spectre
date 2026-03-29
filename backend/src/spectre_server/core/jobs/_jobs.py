# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import time

from ._workers import Worker
from ._duration import Duration

_LOGGER = logging.getLogger(__name__)


class Job:
    def __init__(self, workers: list[Worker]) -> None:
        """Represents a collection of workers that run long-running tasks as
        multiprocessing processes.

        :param workers: A list of `Worker` instances to manage as part of the job.
        """
        self._workers = workers

    @property
    def workers_are_alive(self) -> bool:
        """Returns True if all managed workers are alive, and False otherwise."""
        return all([worker.is_alive for worker in self._workers])

    def start(
        self,
    ) -> None:
        """Tell each worker to call their functions in the background as multiprocessing processes."""
        if self.workers_are_alive:
            raise RuntimeError("A job cannot be started twice.")
        for worker in self._workers:
            worker.start()

    def kill(
        self,
    ) -> None:
        """Tell each worker to kill their processes, if the processes are still running."""
        _LOGGER.info("Killing workers...")
        for worker in self._workers:
            if worker.is_alive:
                worker.kill()

        _LOGGER.info("All workers successfully killed")

    def restart(
        self,
    ) -> None:
        """Tell each worker to restart its process."""
        for worker in self._workers:
            worker.restart()

    def monitor(
        self, duration: float, force_restart: bool = False, max_restarts: int = 5
    ) -> None:
        """
        Monitor the workers during execution and handle unexpected exits.

        Periodically checks worker processes within the specified runtime duration.
        If a worker exits unexpectedly:
        - Restarts all workers if `force_restart` is True.
        - Kills all workers and raises an exception if `force_restart` is False.

        :param duration: Total time to monitor the workers, in seconds.
        :param force_restart: Whether to restart all workers if one dies unexpectedly.
        :param max_restarts: Maximum number of times workers can be restarted before giving up and killing all workers.
        Only applies when force_restart is True. Defaults to 5.
        :raises RuntimeError: If a worker exits and `force_restart` is False.
        """
        _LOGGER.info("Monitoring workers...")
        start_time = time.time()

        restarts_remaining = max_restarts
        try:
            # Check that the elapsed time since the job started is within the total runtime configured by the user.
            while time.time() - start_time < duration:
                for worker in self._workers:
                    if not worker.is_alive:
                        error_message = (
                            f"Worker with name `{worker.name}` unexpectedly exited."
                        )
                        _LOGGER.error(error_message)
                        if force_restart:
                            if restarts_remaining > 0:
                                _LOGGER.info(
                                    f"Attempting restart ({restarts_remaining} restarts remaining)..."
                                )
                                restarts_remaining -= 1
                                self.restart()

                            else:
                                error_message = (
                                    f"Maximum number of restarts has been reached: {max_restarts}. "
                                    f"Killing all workers."
                                )
                                self.kill()
                                raise RuntimeError(error_message)
                        else:
                            self.kill()
                            raise RuntimeError(error_message)
                time.sleep(Duration.ONE_DECISECOND)  # Poll every 0.1 seconds

            # If the jobs total runtime has elapsed, kill all the workers
            _LOGGER.info("Job complete. Killing workers... ")
            self.kill()

        except KeyboardInterrupt:
            _LOGGER.info("Keyboard interrupt detected. Killing workers...")
            self.kill()


def start_job(
    workers: list[Worker],
    duration: float,
    force_restart: bool = False,
    max_restarts: int = 5,
) -> None:
    """Create and run a job with the specified workers.

    Starts the workers, monitors them for the specified runtime, and handles
    unexpected exits according to the `force_restart` policy.

    :param workers: A list of `Worker` instances to include in the job.
    :param duration: Total time to monitor the workers, in seconds.
    :param force_restart: Whether to restart all workers if one dies unexpectedly.
    :param max_restarts: Maximum number of times workers can be restarted before giving up and killing all workers.
    Only applies when force_restart is True. Defaults to 5.
    """
    job = Job(workers)
    job.start()
    job.monitor(duration, force_restart, max_restarts)
