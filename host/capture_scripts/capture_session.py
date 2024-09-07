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

# Helper functions for reading/writing to log files
def write_to_log_file(data: dict, file_path: str) -> None:
    """Writes the provided dictionary to the specified log file."""
    with open(file_path, 'w') as file:
        json.dump(data, file)

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

def log_process(pid: int, status: str) -> None:
    """Logs subprocess PID and status (running, stopped, etc.) to the tracking file."""
    subprocesses = read_from_log_file(CONFIG.path_to_processes_log)
    subprocesses[str(pid)] = status
    write_to_log_file(subprocesses, CONFIG.path_to_processes_log)

def update_process_status(pid: int, status: str) -> None:
    """Updates the status of a specific subprocess in the tracking file."""
    log_process(pid, status)

def wipe_process_tracking_file() -> None:
    """Resets the process tracking log file to contain an empty dictionary."""
    write_to_log_file({}, CONFIG.path_to_processes_log)


# Configure subprocess-specific logging dynamically without global caching
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


def start(command: List[str]) -> None:
    """
    Starts a subprocess and logs its execution in the tracking file and its own log file.
    """
    try:
        # Start the subprocess
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        
        # Log the subprocess as running in the process tracking file
        log_process(process.pid, 'running')

        # Configure and log subprocess-specific logging
        logger = configure_subprocess_logging(process.pid)
        logger.info(f"Subprocess with PID {process.pid} started with command: {' '.join(command)}")

        typer.secho("Subprocess started. Checking status...", fg=typer.colors.BLUE)

        # Give the subprocess time to warm-up
        time.sleep(1)

        # Capture both stdout and stderr even in case of success
        stdout_output, stderr_output = process.communicate()

        # Check if the subprocess has exited with non-zero status
        if process.returncode != 0:
            logger.error(f"Subprocess with PID {process.pid} failed. Stderr: {stderr_output.decode('utf-8')}")
            update_process_status(process.pid, 'failed')
            typer.secho(f"Subprocess with PID {process.pid} failed. Use 'spectre print process-log' to see error details.", fg=typer.colors.RED)
            return

        typer.secho(f"Subprocess with PID {process.pid} started successfully.", fg=typer.colors.GREEN)
        logger.info(f"Subprocess with PID {process.pid} started successfully.")

    except Exception as e:
        logger = configure_subprocess_logging(process.pid)
        logger.error(f"Exception occurred in subprocess with PID {process.pid}: {str(e)}", exc_info=True)
        update_process_status(process.pid, 'failed')

        typer.secho(f"An exception occurred in subprocess with PID {process.pid}. Use 'spectre print process-log' to see error details.", fg=typer.colors.RED)


def stop() -> None:
    """
    Stops all running subprocesses listed in the process tracking file.
    """
    subprocesses = read_from_log_file(CONFIG.path_to_processes_log)

    if not subprocesses:
        typer.secho("No subprocesses found to stop.", fg=typer.colors.YELLOW)
        return

    for pid, status in subprocesses.items():
        if status == 'running':
            try:
                os.kill(int(pid), signal.SIGTERM)
                typer.secho(f"Subprocess with PID {pid} has been successfully terminated.", fg=typer.colors.GREEN)

                # Ensure the process has actually terminated
                time.sleep(1)
                try:
                    os.kill(int(pid), 0)  # Check if the process is still alive
                except ProcessLookupError:
                    # Process is terminated
                    update_process_status(pid, 'stopped')
                    logger = configure_subprocess_logging(int(pid))
                    logger.info(f"Subprocess with PID {pid} has been terminated.")
                else:
                    # Forcefully kill if still alive
                    os.kill(int(pid), signal.SIGKILL)
                    typer.secho(f"Subprocess with PID {pid} was forcefully terminated.", fg=typer.colors.YELLOW)
                    update_process_status(pid, 'killed')
                    logger.info(f"Subprocess with PID {pid} was forcefully killed.")
                    
            except ProcessLookupError:
                typer.secho(f"Failed to terminate subprocess with PID {pid}. It may have already exited.", fg=typer.colors.RED)

    wipe_process_tracking_file()
    typer.secho("All subprocesses have been addressed, and the log file has been cleared.", fg=typer.colors.GREEN)


def has_failure() -> bool:
    """Checks if any subprocess has failed by looking in the tracking file."""
    subprocesses = read_from_log_file(CONFIG.path_to_processes_log)
    return any(status == 'failed' for status in subprocesses.values())
