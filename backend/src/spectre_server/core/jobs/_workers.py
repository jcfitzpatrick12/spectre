# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import time
import typing
import multiprocessing

import spectre_server.core.logs
import spectre_server.core.config
from ._duration import Duration

_LOGGER = logging.getLogger(__name__)


def _make_daemon_process(
    name: str, target: typing.Callable[[], None]
) -> multiprocessing.Process:
    """
    Creates and returns a daemon `multiprocessing.Process` instance.

    :param name: The name to assign to the process.
    :param target: The function to execute in the process.
    :return: A `multiprocessing.Process` instance configured as a daemon.
    """
    return multiprocessing.Process(target=target, name=name, daemon=True)


class Worker:
    def __init__(
        self,
        name: str,
        target: typing.Callable[[], None],
    ) -> None:
        """A lightweight wrapper for a `multiprocessing.Process` daemon.

        Provides a very simple API to start, kill, and restart a multiprocessing process.

        :param name: The name assigned to the process.
        :param target: The callable to be executed by the worker process.
        """
        self._name = name
        self._target = target
        self._process = _make_daemon_process(name, target)

    @property
    def name(self) -> str:
        """Get the name of the worker process.

        :return: The name of the multiprocessing process.
        """
        return self._process.name

    @property
    def is_alive(self) -> bool:
        """Return whether the managed process is alive."""
        return self._process.is_alive()

    @property
    def pid(self) -> int:
        """Get the OS process id of the worker process.

        :raises RuntimeError: if the worker has not been started yet
            (multiprocessing only assigns a pid at `start()` time).
        """
        if self._process.pid is None:
            raise RuntimeError("Worker has not been started.")
        return self._process.pid

    def start(self) -> None:
        """Start the worker process.

        This method runs the `target` in the background as a daemon.
        """
        if self.is_alive:
            raise RuntimeError("A worker cannot be started twice.")

        self._process.start()

    def kill(self) -> None:
        """Kill the managed process."""
        if not self.is_alive:
            raise RuntimeError("Cannot kill a process which is not alive.")

        self._process.kill()

    def restart(self) -> None:
        """Restart the worker process.

        Kills the existing process if it is alive and then starts a new process
        after a brief pause.
        """
        _LOGGER.info(f"Restarting {self.name} worker")
        if self.is_alive:
            # forcibly stop if it is still alive
            self.kill()

        # a moment of respite
        time.sleep(0.5 * Duration.ONE_SECOND)

        # make a new process, as we can't start the same process again.
        self._process = _make_daemon_process(self._name, self._target)
        self.start()


# TODO: Somehow statically type check that `args` match the arguments to `target`
def make_worker(
    name: str,
    target: typing.Callable[..., None],
    args: tuple = (),
    log_file_path: typing.Optional[str] = None,
    spectre_data_dir_path: typing.Optional[str] = None,
) -> Worker:
    """Create a `Worker` instance to manage a target function in a multiprocessing background daemon process.

    This function returns a `Worker` that is configured to run the given target function with the provided arguments
    in a separate process. The worker is not started automatically; you must call `start()` to call the target. The target should not return anything,
    as its return value will be discarded.

    :param name: Human-readable name for the worker process.
    :param target: The function to be executed by the worker process.
    :param args: Arguments to pass to the target function.
    :param log_file_path: If specified, configure the root logger in the worker process to
    write log events to this file. If None, root logger configuration is skipped.
    :param spectre_data_dir_path: If specified, override the `SPECTRE_DATA_DIR_PATH` environment variable to this value in the process
    managed by the worker.
    :return: A `Worker` instance managing the background process (not started).
    """

    def _worker_target() -> None:
        if spectre_data_dir_path is not None:
            spectre_server.core.config.paths.set_spectre_data_dir_path(
                spectre_data_dir_path
            )

        if log_file_path is not None:
            spectre_server.core.logs.configure_root_logger(log_file_path)

        target(*args)

    return Worker(name, _worker_target)
