# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from logging import getLogger
_LOGGER = getLogger(__name__)

import time
from typing import List, Callable, Tuple
import multiprocessing

from spectre.receivers.factory import get_receiver
from spectre.watchdog.watcher import Watcher
from spectre.file_handlers.json_configs import CaptureConfigHandler
from spectre.logging import (
    configure_root_logger, 
    log_service_call
)

# Utility functions
def _calculate_total_runtime(seconds: int = 0, minutes: int = 0, hours: int = 0) -> float:
    return seconds + (minutes * 60) + (hours * 3600)


def _terminate_processes(processes: List[multiprocessing.Process]) -> None:
    _LOGGER.info("Terminating processes..")
    for p in processes:
        if p.is_alive():
            p.terminate()
            p.join()
    _LOGGER.info("All processes successfully terminated")


def start_process(target_func: Callable, 
                  args: tuple, 
                  process_name: str) -> multiprocessing.Process:
    _LOGGER.info(f"Starting {process_name} process..")
    process = multiprocessing.Process(target=target_func, 
                                      args=args, 
                                      name=process_name, 
                                      daemon=True)
    process.start()
    time.sleep(1)  # Allow the process to initialize

    if process.is_alive():
        _LOGGER.info(f"{process_name.capitalize()} process started successfully")
    else:
        _LOGGER.error(f"{process_name.capitalize()} process failed to start")
        process.terminate()
    return process


def _restart_all_processes(process_infos: List[tuple]) -> List[tuple]:
    _LOGGER.info("Restarting all processes..")
    new_process_infos = []
    for process, target_func, args in process_infos:
        new_process = start_process(target_func, args, process.name)
        new_process_infos.append((new_process, target_func, args))
    _LOGGER.info("Processes successfully restarted")
    return new_process_infos


def _monitor_processes(process_infos: List[tuple], 
                       total_runtime: float, 
                       force_restart: bool) -> None:
    _LOGGER.info("Monitoring processes... ")
    start_time = time.time()
    try:
        while time.time() - start_time < total_runtime:
            for process, _, _ in process_infos:
                if not process.is_alive():
                    _LOGGER.error(f"Process {process.name} unexpectedly exited")
                    if force_restart:
                        _terminate_processes([p[0] for p in process_infos])
                        process_infos = _restart_all_processes(process_infos)
                    else:
                        _terminate_processes([p[0] for p in process_infos])
                        return

            time.sleep(1)  # Poll every 1 second
        _LOGGER.info("Session duration reached")
        _terminate_processes([p[0] for p in process_infos])

    except KeyboardInterrupt:
        _LOGGER.info("Keyboard Interrupt detected. Terminating processes")
        _terminate_processes([p[0] for p in process_infos])


def _start_capture(tag: str,
                   do_logging: bool,
                   logging_level: int = logging.INFO,
                   ) -> None:
    
    # load the receiver and mode from the capture config file
    capture_config_handler = CaptureConfigHandler(tag)
    receiver_name, mode = capture_config_handler.get_receiver_metadata()

    if do_logging:  
        configure_root_logger(f"WORKER", 
                              level = logging_level)
    _LOGGER.info(f"Starting capture with the receiver: {receiver_name} operating in mode: {mode} with tag: {tag}")
    try:
        receiver = get_receiver(receiver_name, mode=mode)
        receiver.start_capture(tag)
    except:
        _LOGGER.error("An error has occured during capture", exc_info=True)
        raise


def _start_watcher(tag: str,
                   do_logging: bool = False,
                   logging_level: int = logging.INFO) -> None:
    if do_logging:
        configure_root_logger(f"WORKER", level = logging_level) #  start worker log
    _LOGGER.info(f"Starting watcher with tag: {tag}")
    watcher = Watcher(tag)
    watcher.start()


def _get_user_root_logger_state() -> Tuple[bool, int]:
    """Get the state of the users root logger """
    user_root_logger = getLogger() # no name implies returning of the root logger
    if user_root_logger.handlers:
        is_logging = True
        level = user_root_logger.level
        return is_logging, level
    else:
        is_logging = False
        level = None
        return (is_logging, level)


@log_service_call(_LOGGER)
def start(tag: str, 
          seconds: int = 0, 
          minutes: int = 0, 
          hours: int = 0, 
          force_restart: bool = False) -> None:
    
    if seconds == 0 and minutes == 0 and hours == 0:
        raise ValueError(f"Session duration must be specified")
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)

    # evaluate the user root logger state, so we can propagate it to the worker processes
    do_logging, logging_level = _get_user_root_logger_state()

    capture_args = (
        tag,
        do_logging,
        logging_level
    )
    capture_process = start_process(_start_capture, 
                                    capture_args, 
                                    "capture")
    _monitor_processes([(capture_process, _start_capture, capture_args)], total_runtime, force_restart)


@log_service_call(_LOGGER)
def session(tag: str, 
            force_restart: bool = False, 
            seconds: int = 0, 
            minutes: int = 0, 
            hours: int = 0) -> None:
    
    if seconds == 0 and minutes == 0 and hours == 0:
        raise ValueError(f"Session duration must be specified")
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)

    # evaluate the user root logger state, so we can propagate it to the worker processes
    do_logging, logging_level = _get_user_root_logger_state()

    watcher_args = (
        tag,
        do_logging,
        logging_level
    )
    watcher_process = start_process(_start_watcher, 
                                    watcher_args, 
                                    "watcher")

    capture_args = (
        tag,
        do_logging,
        logging_level
    )
    capture_process = start_process(_start_capture, 
                                    capture_args, 
                                    "capture")

    if not watcher_process.is_alive() or not capture_process.is_alive():
        _terminate_processes([watcher_process, capture_process])
        return

    _monitor_processes([(watcher_process, _start_watcher, watcher_args),
                        (capture_process, _start_capture, capture_args)], 
                        total_runtime, 
                        force_restart)
    