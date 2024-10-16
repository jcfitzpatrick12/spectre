# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from logging import getLogger
_LOGGER = getLogger(__name__)

import multiprocessing

import time
from typing import List

from spectre.receivers.factory import get_receiver
from spectre.watchdog.watcher import Watcher
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


def start_process(target_func, 
                  args: tuple, 
                  process_name: str) -> multiprocessing.Process:
    _LOGGER.info("Starting {process_name} process..")
    process = multiprocessing.Process(target=target_func, args=args, name=process_name, daemon=True)
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


def configure_logger(filename):
    """Configure logger with a specific filename."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # Remove any existing handlers to avoid duplicate logs
    for handler in logger.handlers:
        logger.removeHandler(handler)
    # Set up file handler with specific filename
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(processName)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def _start_capture(receiver_name: str, 
                   mode: str, 
                   tags: List[str]) -> None:
    from spectre.cfg import LOGS_DIR_PATH
    configure_logger(f"{LOGS_DIR_PATH}/2024/10/16/test.log")
    _LOGGER.info(f"Starting capture with the receiver: {receiver_name} operating in mode: {mode} with tags: {tags}")
    receiver = get_receiver(receiver_name, mode=mode)
    receiver.start_capture(tags)


def _start_watcher(tags: List[str]) -> None:
    configure_root_logger("WORKER") #  start worker log
    _LOGGER.info(f"Starting watcher with tags {tags}")
    for tag in tags:
        watcher = Watcher(tag)
        watcher.start()


@log_service_call(_LOGGER)
def start(receiver_name: str, 
          mode: str, 
          tags: List[str], 
          seconds: int = 0, minutes: int = 0, 
          hours: int = 0, 
          force_restart: bool = False) -> None:
    if seconds == 0 and minutes == 0 and hours == 0:
        raise ValueError(f"Session duration must be specified")
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)
    capture_process = start_process(_start_capture, (receiver_name, mode, tags), "capture")
    _monitor_processes([(capture_process, _start_capture, (receiver_name, mode, tags))], total_runtime, force_restart)


@log_service_call(_LOGGER)
def session(receiver_name: str,
            mode: str, 
            tags: List[str], 
            force_restart: bool = False, 
            seconds: int = 0, 
            minutes: int = 0, 
            hours: int = 0) -> None:
    if seconds == 0 and minutes == 0 and hours == 0:
        raise ValueError(f"Session duration must be specified")
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)
    watcher_process = start_process(_start_watcher, (tags,), "watcher")
    capture_process = start_process(_start_capture, (receiver_name, mode, tags), "capture")

    if not watcher_process.is_alive() or not capture_process.is_alive():
        _terminate_processes([watcher_process, capture_process])
        return

    _monitor_processes([(watcher_process, _start_watcher, (tags,)),
                        (capture_process, _start_capture, (receiver_name, mode, tags))], total_runtime, force_restart)
    