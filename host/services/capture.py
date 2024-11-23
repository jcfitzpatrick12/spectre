# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import Any
import time
from typing import List, Callable, Tuple
import multiprocessing

from spectre.receivers.factory import get_receiver
from spectre.watchdog.watcher import Watcher
from spectre.file_handlers.json_configs import CaptureConfigHandler
from spectre.logging import (
    configure_root_logger, 
    log_call
)

class _ProcessWrapper:
    """Encapsulates a process and its callable information"""
    def __init__(self,
                 process: multiprocessing.Process,
                 target_func: Callable,
                 target_func_args: Tuple[Any, ...]):
        self._process = process
        self._target_func = target_func
        self._target_func_args = target_func_args


    @property
    def process(self) -> multiprocessing.Process:
        return self._process
    

    @staticmethod
    def start(target: Callable, 
              args: Tuple[Any, ...], 
              name: str) -> '_ProcessWrapper':
        """Start a new process"""
        _LOGGER.info(f"Starting {name} process..")
        process = multiprocessing.Process(target=target, 
                                          args=args,  
                                          name=name, 
                                          daemon=True)
        process.start()
        return _ProcessWrapper(process, 
                               target, 
                               args)
    

    def restart(self) -> None:
        """Restart the encapsulated process"""
        _LOGGER.info(f"Restarting {self._process.name} process")
        if self._process.is_alive():
            # forcibly stop if it is still alive
            self._process.terminate()
            self._process.join()
        # a moment of respite
        time.sleep(1)
        self._process = multiprocessing.Process(target=self._target_func, 
                                                args=self._target_func_args, 
                                                name=self.process.name, 
                                                daemon=True)
        self._process.start()


def _terminate_processes(process_wrappers: List[_ProcessWrapper]) -> None:
    """Terminate all given processes"""
    _LOGGER.info("Terminating processes...")
    for wrapper in process_wrappers:
        if wrapper.process.is_alive():
            wrapper.process.terminate()
            wrapper.process.join()
    _LOGGER.info("All processes successfully terminated")


def _monitor_processes(process_wrappers: List[_ProcessWrapper], 
                       total_runtime: float, 
                       force_restart: bool) -> None:
    """Monitor and restart processes if necessary."""
    _LOGGER.info("Monitoring processes...")
    start_time = time.time()

    try:
        while time.time() - start_time < total_runtime:
            for wrapper in process_wrappers:
                if not wrapper.process.is_alive():
                    _LOGGER.error(f"Process {wrapper.process.name} unexpectedly exited")
                    if force_restart:
                        # restart all processes
                        for wrapper in process_wrappers:
                            wrapper.restart()
                    else:
                        _terminate_processes(process_wrappers)
                        return
            time.sleep(1)  # Poll every second
        _LOGGER.info("Session duration reached")
        _terminate_processes(process_wrappers)
    except KeyboardInterrupt:
        _LOGGER.info("Keyboard interrupt detected. Terminating processes")
        _terminate_processes(process_wrappers)


def _calculate_total_runtime(seconds: int = 0, minutes: int = 0, hours: int = 0) -> float:
    """Calculate total runtime in seconds"""
    if seconds == 0 and minutes == 0 and hours == 0:
        raise ValueError(f"Session duration must be specified")
    return seconds + (minutes * 60) + (hours * 3600)


def _get_user_root_logger_state() -> Tuple[bool, int]:
    """Check the state of the user's root logger"""
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return True, root_logger.level
    return False, logging.NOTSET


def _start_capture(tag: str,
                   do_logging: bool,
                   logging_level: int = logging.INFO) -> None:
    
    # load the receiver and mode from the capture config file
    capture_config_handler = CaptureConfigHandler(tag)
    receiver_name, mode = capture_config_handler.get_receiver_metadata()

    if do_logging:  
        configure_root_logger(f"WORKER", 
                              level = logging_level)
    _LOGGER.info((f"Starting capture with the receiver: {receiver_name} "
                  f"operating in mode: {mode} "
                  f"with tag: {tag}"))

    receiver = get_receiver(receiver_name, mode=mode)
    receiver.start_capture(tag)


def _start_watcher(tag: str,
                   do_logging: bool = False,
                   logging_level: int = logging.INFO) -> None:
    if do_logging:
        configure_root_logger(f"WORKER", level = logging_level) #  start worker log
    _LOGGER.info(f"Starting watcher with tag: {tag}")
    watcher = Watcher(tag)
    watcher.start()


@log_call(_LOGGER)
def start(tag: str, 
          seconds: int = 0, 
          minutes: int = 0, 
          hours: int = 0, 
          force_restart: bool = False) -> None:

    total_runtime = _calculate_total_runtime(seconds, 
                                             minutes, 
                                             hours) 

    # evaluate the user root logger state, so we can propagate it to the worker processes
    do_logging, logging_level = _get_user_root_logger_state()

    capture_args = (
        tag,
        do_logging,
        logging_level
    )
    capture_process = _ProcessWrapper.start(_start_capture, 
                                            capture_args, 
                                            "capture")
    _monitor_processes([capture_process], 
                       total_runtime, 
                       force_restart)


@log_call(_LOGGER)
def session(tag: str, 
            force_restart: bool = False, 
            seconds: int = 0, 
            minutes: int = 0, 
            hours: int = 0) -> None:
    
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)

    # evaluate the user root logger state, so we can propagate it to the worker processes
    do_logging, logging_level = _get_user_root_logger_state()

    watcher_args = (
        tag,
        do_logging,
        logging_level
    )
    watcher_process = _ProcessWrapper.start(_start_watcher, 
                                            watcher_args, 
                                            "watcher")

    capture_args = (
        tag,
        do_logging,
        logging_level
    )
    capture_process = _ProcessWrapper.start(_start_capture, 
                                            capture_args, 
                                            "capture")

    _monitor_processes([watcher_process, capture_process], 
                        total_runtime, 
                        force_restart)
    