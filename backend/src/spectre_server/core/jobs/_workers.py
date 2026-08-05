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
        on_start: typing.Optional[typing.Callable[[int], None]] = None,
    ) -> None:
        """A lightweight wrapper for a `multiprocessing.Process` daemon.

        Provides a very simple API to start, kill, and restart a multiprocessing process.

        :param name: The name assigned to the process.
        :param target: The callable to be executed by the worker process.
        :param on_start: Optional callback invoked after every successful
            ``start()`` (including implicit starts from ``restart()``) with the
            fresh OS PID. Exceptions from the callback propagate to the caller.
        """
        self._name = name
        self._target = target
        self._on_start = on_start
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

        Runs the `target` in the background as a daemon. If an ``on_start``
        callback was supplied, it is invoked with the fresh PID after the
        child has been spawned.
        """
        if self.is_alive:
            raise RuntimeError("A worker cannot be started twice.")

        self._process.start()
        if self._on_start is not None:
            self._on_start(self.pid)

    def kill(self) -> None:
        """Kill the managed process."""
        if not self.is_alive:
            raise RuntimeError("Cannot kill a process which is not alive.")

        self._process.kill()

    def restart(self) -> None:
        """Restart the worker process.

        Kills the existing process if still alive, then spawns a fresh one
        (a ``multiprocessing.Process`` cannot be started twice).
        """
        _LOGGER.info(f"Restarting {self.name} worker")
        if self.is_alive:
            self.kill()

        time.sleep(0.5 * Duration.ONE_SECOND)

        self._process = _make_daemon_process(self._name, self._target)
        self.start()


# TODO: Somehow statically type check that `args` match the arguments to `target`
def make_worker(
    name: str,
    target: typing.Callable[..., None],
    args: tuple = (),
    configure_logging: bool = True,
    spectre_data_dir_path: typing.Optional[str] = None,
    on_start: typing.Optional[typing.Callable[[int], None]] = None,
) -> Worker:
    """Create a `Worker` that runs ``target`` in a daemon subprocess.

    The worker is not started automatically; the caller must invoke ``start()``
    (or hand it to a ``Job``). The target should not return anything, as its
    return value will be discarded.

    :param name: Human-readable name for the worker process.
    :param target: The function to be executed by the worker process.
    :param args: Arguments to pass to the target function.
    :param configure_logging: If True, configure the root logger inside the
        subprocess so log events are written to file. Defaults to True.
    :param spectre_data_dir_path: If specified, override ``SPECTRE_DATA_DIR_PATH``
        inside the subprocess to this value.
    :param on_start: Optional callback invoked in the parent process after
        every successful ``start()`` (including restarts) with the fresh PID.
    :return: A `Worker` instance managing the background process (not started).
    """

    def _worker_target() -> None:
        if spectre_data_dir_path is not None:
            spectre_server.core.config.paths.set_spectre_data_dir_path(
                spectre_data_dir_path
            )

        if configure_logging:
            spectre_server.core.logs.configure_root_logger(
                spectre_server.core.logs.ProcessType.WORKER,
            )

        target(*args)

    return Worker(name, _worker_target, on_start=on_start)
