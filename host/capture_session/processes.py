# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
import json
import os
import signal
import time
import logging
from logging import FileHandler, Formatter
import typer
from typing import List

from cfg import CONFIG


def read_process_log() -> dict:
    try:
        with open(CONFIG.path_to_processes_log, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def write_to_process_log(data: dict) -> None:
    with open(CONFIG.path_to_processes_log, 'w') as file:
        json.dump(data, file)


# Function to log and update subprocess statuses in the tracking file
def update_process_log(pid: int, status: str) -> None:
    subprocesses = read_process_log()
    subprocesses[str(pid)] = status
    write_to_process_log(subprocesses)


# Function to configure logging for each subprocess
def configure_subprocess_logging(pid: int) -> logging.Logger:
    log_file = os.path.join(CONFIG.path_to_logs, f"subprocess_{pid}.log")
    logger = logging.getLogger(f"subprocess_{pid}")
    if not logger.handlers:  # Avoid adding multiple handlers
        file_handler = FileHandler(log_file)
        file_handler.setFormatter(Formatter('%(asctime)s:%(levelname)s:%(message)s'))
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
    return logger

def is_process_running(pid: int) -> bool:
    # checks if a process with the given PID is still running using os.kill with signal 0
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def update_subprocess_statuses() -> None:
    # Read subprocesses from the log file
    subprocesses = read_process_log()

    if not subprocesses:
        typer.secho("No subprocesses found to update.", fg=typer.colors.YELLOW)
        return

    for pid_str, status in subprocesses.items():
        pid = int(pid_str)
        logger = configure_subprocess_logging(pid)

        # Skip if already marked as failed
        if status == 'failed':
            continue

        # Update process status based on whether it's running or stopped
        update_status_for_pid(pid, logger)

    typer.secho("Subprocess statuses have been updated.", fg=typer.colors.GREEN)


def update_status_for_pid(pid: int, logger) -> None:    
    # Check if the process is still running
    if is_process_running(pid):
        logger.info(f"The subprocess with PID {pid} is still running.")
        return

    # Process has stopped, check its exit status
    try:
        pid, wait_result = os.waitpid(pid, os.WNOHANG)
        exit_code = os.WEXITSTATUS(wait_result)

        if exit_code == 0: # exit is success
            update_process_log(pid, 'stopped')
            logger.info(f"Subprocess with PID {pid} exited successfully.")
        else: # exit code is not a success
            update_process_log(pid, 'failed')
            logger.error(f"Subprocess with PID {pid} failed with exit code {exit_code}.")
    except ChildProcessError:
        # Process is already reaped by the system, mark it as reaped
        update_process_log(pid, 'stopped')
        logger.info(f"Subprocess with PID {pid} has already been reaped by the system.")



# Function to start a subprocess and track its status
def start(command: List[str]) -> None:
    # execute the command as a subprocess
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    update_process_log(process.pid, 'running')
    typer.secho(f"Subprocess with PID {process.pid} started. Checking status...", fg=typer.colors.BLUE)
    # give the subprocess time to boot up
    time.sleep(1)

    if process.poll() is not None:
        typer.secho(f"Subprocess with PID {process.pid} failed shortly after starting. Use \"spectre print process-log --pid <pid>\" to find out more.", fg=typer.colors.RED)
        update_process_log(process.pid, 'failed')
        raise typer.Exit(1)

    typer.secho(f"Subprocess with PID {process.pid} started successfully.", fg=typer.colors.GREEN)


def stop() -> None:
    subprocesses = read_process_log()

    if not subprocesses:
        typer.secho("No subprocesses found to stop.", fg=typer.colors.YELLOW)
        return

    for pid_str, status in subprocesses.items():
        pid = int(pid_str)
        logger = configure_subprocess_logging(pid)

        if status == 'running':
            try:
                os.kill(pid, signal.SIGKILL)  # Immediately forcefully terminate the process
                typer.secho(f"Subprocess with PID {pid} has been terminated.", fg=typer.colors.GREEN)
                logger.info(f"Subprocess with PID {pid} has been terminated.")
                update_process_log(pid, 'killed')

            except ProcessLookupError:
                typer.secho(f"Subprocess with PID {pid} was not found. It may have already exited.", fg=typer.colors.RED)

    typer.secho("All subprocesses have been forcefully terminated.", fg=typer.colors.GREEN)
    write_to_process_log({})  # Clear the log after termination


# Check if any subprocess is not running
def any_process_not_running() -> bool:
    process_log = read_process_log()
    for _, status in process_log.items():
        if status != 'running':
            return True
    return False

