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

from spectre_core.logging import log_call
from spectre_core.receivers.factory import get_receiver
from spectre_core.post_processing.post_processor import PostProcessor
from spectre_core.capture_config import CaptureConfig
from spectre_core.logging import (
    configure_root_logger, 
    log_call
)


class _Worker:
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
    

    @property
    def name(self) -> str:
        return self._process.name


    def restart(self) -> None:
        """Restart the encapsulated process"""
        _LOGGER.info(f"Restarting {self.name} worker")
        if self._process.is_alive():
            # forcibly stop if it is still alive
            self._process.terminate()
            self._process.join()
        # a moment of respite
        time.sleep(1)
        self._process = multiprocessing.Process(target=self._target_func, 
                                                args=self._target_func_args, 
                                                name=self.name, 
                                                daemon=True)
        self._process.start()


def start_worker(target: Callable, 
                 args: Tuple[Any, ...], 
                 name: str
) -> _Worker:
    """Start a new worker process"""
    _LOGGER.info(f"Starting {name} worker...")

    process = multiprocessing.Process(target=target,
                                      args=args,
                                      name=name,
                                      daemon=True)

    process.start()
    
    # return a wrapper, which will allow us to simply restart the process
    return _Worker(process, 
                   target, 
                   args)


def _terminate_workers(workers: List[_Worker]) -> None:
    """Terminate all given worker processes"""
    _LOGGER.info("Terminating workers...")
    for worker in workers:
        if worker.process.is_alive():
           worker.process.terminate()
           worker.process.join()
    _LOGGER.info("All workers successfully terminated")


def _monitor_workers(workers: List[_Worker], 
                     total_runtime: float, 
                     force_restart: bool
) -> None:
    """Monitor worker processes"""
    _LOGGER.info("Monitoring workers...")
    start_time = time.time()

    try:
        while time.time() - start_time < total_runtime:
            for worker in workers:
                if not worker.process.is_alive():
                    error_message = f"Worker with name `{worker.name}` unexpectedly exited"
                    _LOGGER.error(error_message)
                    if force_restart:
                        # restart all processes
                        for worker in workers:
                            worker.restart()
                    else:
                        _terminate_workers(workers)
                        raise RuntimeError(error_message)
            time.sleep(1)  # Poll every second
        _LOGGER.info("Session duration reached")
        _terminate_workers(workers)
    except KeyboardInterrupt:
        _LOGGER.info("Keyboard interrupt detected. Terminating workers")
        _terminate_workers(workers)
    

def _calculate_total_runtime(seconds: int = 0, 
                             minutes: int = 0, 
                             hours: int = 0
) -> float:
    """Calculate total runtime in seconds"""
    total_duration = seconds + (minutes * 60) + (hours * 3600) # [s]
    if total_duration <= 0:
        raise ValueError(f"Total duration must be strictly positive")
    return total_duration


def _get_user_root_logger_state(
) -> Tuple[bool, int]:
    """Check the state of the user's root logger"""
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return True, root_logger.level
    return False, logging.NOTSET


@log_call
def _start_capture(tag: str,
                   do_logging: bool,
                   logging_level: int = logging.INFO
) -> None:

    if do_logging:  
        configure_root_logger(f"worker", 
                              level = logging_level) 

    _LOGGER.info((f"Reading capture config with tag `{tag}`"))

    # load the receiver and mode from the capture config file
    capture_config = CaptureConfig(tag)

    _LOGGER.info((f"Starting capture with the receiver `{capture_config.receiver_name}` "
                  f"operating in mode `{capture_config.receiver_mode}` "
                  f"with tag `{tag}`"))

    receiver = get_receiver(capture_config.receiver_name, 
                            mode=capture_config.receiver_mode)
    receiver.start_capture(tag)


@log_call
def _start_post_processor(tag: str,
                   do_logging: bool = False,
                   logging_level: int = logging.INFO
) -> None:
    if do_logging:
        configure_root_logger(f"worker", level = logging_level)
    _LOGGER.info(f"Starting post processor with tag: {tag}")
    post_processor = PostProcessor(tag)
    post_processor.start()


@log_call
def capture(tag: str, 
            seconds: int = 0, 
            minutes: int = 0, 
            hours: int = 0, 
            force_restart: bool = False
) -> None:

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
    capture_worker = start_worker(_start_capture, 
                                    capture_args, 
                                    "capture")
    
    _monitor_workers([capture_worker], 
                     total_runtime, 
                     force_restart)
                       


@log_call
def session(tag: str, 
            seconds: int = 0, 
            minutes: int = 0, 
            hours: int = 0, 
            force_restart: bool = False
) -> None:
    
    total_runtime = _calculate_total_runtime(seconds, 
                                             minutes, 
                                             hours)

    # evaluate the user root logger state, so we can propagate it to the worker processes
    do_logging, logging_level = _get_user_root_logger_state()

    post_processor_args = (
        tag,
        do_logging,
        logging_level
    )
    post_processor_worker = start_worker(_start_post_processor, 
                                         post_processor_args, 
                                         "post_processor")

    capture_args = (
        tag,
        do_logging,
        logging_level
    )
    capture_worker = start_worker(_start_capture, 
                                  capture_args, 
                                  "capture")

    _monitor_workers([post_processor_worker, capture_worker], 
                     total_runtime, 
                     force_restart)
    