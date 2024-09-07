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

        # Skip if already marked as failed
        if status == 'failed':
            logger.info(f"Subprocess with PID {pid} has already failed. Skipping update.")
            continue

        # Check if the process is still running
        if is_process_running(pid):
            logger.info(f"Subprocess with PID {pid} is still running.")
            continue

        # Process has stopped, check its exit status
        try:
            pid, status_code = os.waitpid(pid, os.WNOHANG)
            exit_code = os.WEXITSTATUS(status_code)

            if exit_code == 0:
                update_process_log(pid, 'stopped')
                logger.info(f"Subprocess with PID {pid} exited successfully.")
            else:
                update_process_log(pid, 'failed')
                logger.error(f"Subprocess with PID {pid} failed with exit code {exit_code}.")
        except ChildProcessError:
            # Process is already reaped by the system, mark it as stopped
            update_process_log(pid, 'stopped')
            logger.info(f"Subprocess with PID {pid} has already been reaped by the system.")

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
                os.kill(pid, signal.SIGTERM)  # Send SIGTERM to terminate gracefully
                typer.secho(f"Subprocess with PID {pid} termination initiated.", fg=typer.colors.GREEN)

                # Wait for 1 seconds to give the process time to terminate
                time.sleep(1)

                if not is_process_running(pid):
                    # Process terminated normally
                    update_process_log(pid, 'stopped')
                    logger.info(f"Subprocess with PID {pid} has been stopped.")
                else:
                    # If still running, forcefully terminate with SIGKILL
                    os.kill(pid, signal.SIGKILL)
                    typer.secho(f"Subprocess with PID {pid} was forcefully terminated.", fg=typer.colors.YELLOW)
                    update_process_log(pid, 'killed')

            except ProcessLookupError:
                # If the process is already gone
                typer.secho(f"Failed to terminate subprocess with PID {pid}. It may have already exited.", fg=typer.colors.RED)

    typer.secho("All subprocesses have been addressed, and the log file has been cleared.", fg=typer.colors.GREEN)
    write_to_log_file({}, CONFIG.path_to_processes_log)

# Function to check if any subprocess has failed
def has_failure() -> bool:
    """Checks if any subprocess has failed by looking in the tracking file."""
    subprocesses = read_from_log_file(CONFIG.path_to_processes_log)
    return any(status == 'failed' for status in subprocesses.values())
