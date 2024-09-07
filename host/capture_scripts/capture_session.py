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

# Helper function to write to the log file
def write_to_log_file(data: dict, file_path: str) -> None:
    """Writes the provided dictionary to the specified log file."""
    with open(file_path, 'w') as file:
        json.dump(data, file)

# Helper function to read from the log file
def read_from_log_file(file_path: str) -> dict:
    """Reads from the specified log file and returns a dictionary."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        typer.secho(f"{file_path} not found. Creating and initializing with an empty dictionary.", fg=typer.colors.YELLOW)
        return {}
    except json.JSONDecodeError:
        typer.secho(f"Invalid JSON in {file_path}. Initializing with an empty dictionary.", fg=typer.colors.RED)
        return {}

# Function to log the process information in the tracking file
def log_process(pid: int, status: str) -> None:
    """Logs subprocess PID and status (running, stopped, etc.) to the tracking file."""
    subprocesses = read_from_log_file(CONFIG.path_to_processes_log)
    subprocesses[str(pid)] = status
    write_to_log_file(subprocesses, CONFIG.path_to_processes_log)

# Function to update the process status
def update_process_status(pid: int, status: str) -> None:
    """Updates the status of a specific subprocess in the tracking file."""
    log_process(pid, status)

# Function to reset the process tracking log
def wipe_process_tracking_file() -> None:
    """Resets the process tracking log file to contain an empty dictionary."""
    write_to_log_file({}, CONFIG.path_to_processes_log)

# Function to configure logging for each subprocess
def configure_subprocess_logging(pid: int) -> logging.Logger:
    """Configures and returns a logger for the subprocess, with a log file named after the process PID."""
    log_file = os.path.join(CONFIG.path_to_logs, f"subprocess_{pid}.log")
    logger = logging.getLogger(f"subprocess_{pid}")
    logger.setLevel(logging.INFO)

    # Avoid adding multiple handlers by checking if already set
    if not logger.handlers:
        file_handler = FileHandler(log_file)
        formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Helper function to check if a process is running
def is_process_running(pid: int) -> bool:
    """
    Checks if a process with the given PID is still running.
    Uses os.kill with signal 0 to determine if the process exists.
    """
    try:
        os.kill(pid, 0)  # Signal 0 does not terminate the process, it just checks if it exists
    except OSError:
        return False  # Process is not running
    return True  # Process is running


# Function to update the statuses of subprocesses
def update_subprocess_statuses() -> None:
    """
    Iterates through the subprocesses in the tracking file, checks their status using os.kill(),
    and updates the status if any subprocess has stopped or failed.
    Skips updating processes that are already marked as 'failed'.
    """
    subprocesses = read_from_log_file(CONFIG.path_to_processes_log)

    if not subprocesses:
        typer.secho("No subprocesses found to update.", fg=typer.colors.YELLOW)
        return

    for pid_str, status in subprocesses.items():
        pid = int(pid_str)
        logger = configure_subprocess_logging(pid)

        # Skip updating if the status is 'failed'
        if status == 'failed':
            logger.info(f"Subprocess with PID {pid} has already failed. Skipping update.")
            continue

        # Check if the process is still running
        if is_process_running(pid):
            logger.info(f"Subprocess with PID {pid} is still running.")
        else:
            # Update the status to 'stopped' if the process has stopped
            update_process_status(pid, 'stopped')
            logger.info(f"Subprocess with PID {pid} has stopped or no longer exists.")

    typer.secho("Subprocess statuses have been updated.", fg=typer.colors.GREEN)


def start(command: List[str]) -> None:
    """
    Starts a subprocess and logs its execution in the tracking file.
    Detects and logs if the subprocess fails within the first second.
    """

    # Start the subprocess with no output redirection (same as old version)
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

    # Log the subprocess as running in the process tracking file
    log_process(process.pid, 'running')
    typer.secho(f"Subprocess with PID {process.pid} started. Checking status...", fg=typer.colors.BLUE)

    # Give the subprocess a short time to initialize
    time.sleep(1)

    # Check if the process has exited early using poll()
    if process.poll() is not None:  # The process has exited early
        # Handle early failure
        typer.secho(f"Subprocess with PID {process.pid} failed shortly after starting. Run \"spectre print process-log\" for more details.", fg=typer.colors.RED)
        update_process_status(process.pid, 'failed')
        raise typer.Exit(1)

    # If it's still running after the initial check, mark it as successfully started
    typer.secho(f"Subprocess with PID {process.pid} started successfully.", fg=typer.colors.GREEN)
    log_process(process.pid, 'running')  # Update log to show process is still running


# Function to stop all running subprocesses
def stop() -> None:
    """
    Stops all running subprocesses listed in the process tracking file.
    """
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
                typer.secho(f"Subprocess with PID {pid} has been successfully terminated.", fg=typer.colors.GREEN)

                # Ensure the process has actually terminated
                time.sleep(1)
                if not is_process_running(pid):
                    update_process_status(pid, 'stopped')
                    logger.info(f"Subprocess with PID {pid} has been terminated.")
                else:
                    # Forcefully kill if still alive
                    os.kill(pid, signal.SIGKILL)
                    typer.secho(f"Subprocess with PID {pid} was forcefully terminated.", fg=typer.colors.YELLOW)
                    update_process_status(pid, 'killed')
                    logger.info(f"Subprocess with PID {pid} was forcefully killed.")
                    
            except ProcessLookupError:
                typer.secho(f"Failed to terminate subprocess with PID {pid}. It may have already exited.", fg=typer.colors.RED)

    wipe_process_tracking_file()
    typer.secho("All subprocesses have been addressed, and the log file has been cleared.", fg=typer.colors.GREEN)

# Function to check if any subprocess has failed
def has_failure() -> bool:
    """Checks if any subprocess has failed by looking in the tracking file."""
    subprocesses = read_from_log_file(CONFIG.path_to_processes_log)
    return any(status == 'failed' for status in subprocesses.values())
