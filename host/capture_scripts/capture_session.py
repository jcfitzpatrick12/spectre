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

# Helper function to write/read from the log file
def read_from_log_file(file_path: str) -> dict:
    """Reads and returns a dictionary from the specified log file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        typer.secho(f"{file_path} not found. Initializing with an empty dictionary.", fg=typer.colors.YELLOW)
        return {}
    except json.JSONDecodeError:
        typer.secho(f"Invalid JSON in {file_path}. Initializing with an empty dictionary.", fg=typer.colors.RED)
        return {}

def write_to_log_file(data: dict, file_path: str) -> None:
    """Writes the provided dictionary to the specified log file."""
    with open(file_path, 'w') as file:
        json.dump(data, file)

# Function to log and update subprocess statuses in the tracking file
def update_process_log(pid: int, status: str) -> None:
    """Updates the status of a specific subprocess in the tracking file."""
    subprocesses = read_from_log_file(CONFIG.path_to_processes_log)
    subprocesses[str(pid)] = status
    write_to_log_file(subprocesses, CONFIG.path_to_processes_log)

# Function to configure logging for each subprocess
def configure_subprocess_logging(pid: int) -> logging.Logger:
    """Configures and returns a logger for the subprocess, with a log file named after the process PID."""
    log_file = os.path.join(CONFIG.path_to_logs, f"subprocess_{pid}.log")
    logger = logging.getLogger(f"subprocess_{pid}")
    if not logger.handlers:  # Avoid adding multiple handlers
        file_handler = FileHandler(log_file)
        file_handler.setFormatter(Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
    return logger

# Helper function to check if a process is running
def is_process_running(pid: int) -> bool:
    """Checks if a process with the given PID is still running using os.kill with signal 0."""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

# Function to update the statuses of subprocesses
def update_subprocess_statuses() -> None:
    """Checks and updates the status of all subprocesses, skipping those marked as 'failed'."""
    subprocesses = read_from_log_file(CONFIG.path_to_processes_log)
    if not subprocesses:
        typer.secho("No subprocesses found to update.", fg=typer.colors.YELLOW)
        return

    for pid_str, status in subprocesses.items():
        pid = int(pid_str)
        logger = configure_subprocess_logging(pid)

        if status == 'failed':
            logger.info(f"Subprocess with PID {pid} has already failed. Skipping update.")
            continue

        if is_process_running(pid):
            logger.info(f"Subprocess with PID {pid} is still running.")
        else:
            update_process_log(pid, 'stopped')
            logger.info(f"Subprocess with PID {pid} has stopped or no longer exists.")

    typer.secho("Subprocess statuses have been updated.", fg=typer.colors.GREEN)

# Function to start a subprocess and track its status
def start(command: List[str]) -> None:
    """Starts a subprocess and logs its status, detecting early failures."""
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    update_process_log(process.pid, 'running')
    typer.secho(f"Subprocess with PID {process.pid} started. Checking status...", fg=typer.colors.BLUE)

    time.sleep(1)

    if process.poll() is not None:
        typer.secho(f"Subprocess with PID {process.pid} failed shortly after starting.", fg=typer.colors.RED)
        update_process_log(process.pid, 'failed')
        raise typer.Exit(1)

    typer.secho(f"Subprocess with PID {process.pid} started successfully.", fg=typer.colors.GREEN)

# Function to stop all running subprocesses
def stop() -> None:
    """Stops all running subprocesses listed in the process tracking file."""
    subprocesses = read_from_log_file(CONFIG.path_to_processes_log)

    if not subprocesses:
        typer.secho("No subprocesses found to stop.", fg=typer.colors.YELLOW)
        return

    for pid_str, status in subprocesses.items():
        pid = int(pid_str)
        logger = configure_subprocess_logging(pid)

        if status == 'running':
            try:
                os.kill(pid, signal.SIGTERM)
                typer.secho(f"Subprocess with PID {pid} terminated.", fg=typer.colors.GREEN)
                time.sleep(1)
                if not is_process_running(pid):
                    update_process_log(pid, 'stopped')
                    logger.info(f"Subprocess with PID {pid} has been stopped.")
                else:
                    os.kill(pid, signal.SIGKILL)
                    typer.secho(f"Subprocess with PID {pid} was forcefully terminated.", fg=typer.colors.YELLOW)
                    update_process_log(pid, 'killed')
            except ProcessLookupError:
                typer.secho(f"Failed to terminate subprocess with PID {pid}. It may have already exited.", fg=typer.colors.RED)

    typer.secho("All subprocesses have been addressed, and the log file has been cleared.", fg=typer.colors.GREEN)
    write_to_log_file({}, CONFIG.path_to_processes_log)

# Function to check if any subprocess has failed
def has_failure() -> bool:
    """Checks if any subprocess has failed by looking in the tracking file."""
    subprocesses = read_from_log_file(CONFIG.path_to_processes_log)
    return any(status == 'failed' for status in subprocesses.values())
