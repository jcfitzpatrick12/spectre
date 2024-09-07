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

# Global cache for subprocess loggers
subprocess_loggers = {}

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
        write_to_log_file({}, file_path)
        return {}
    except json.JSONDecodeError:
        typer.secho(f"Invalid JSON in {file_path}. Initializing with an empty dictionary.", fg=typer.colors.RED)
        write_to_log_file({}, file_path)
        return {}

# Configure and cache subprocess-specific loggers
def configure_subprocess_logging(pid: int) -> logging.Logger:
    """
    Configures and returns a logger for the subprocess, with a log file named after the process PID.
    Caches the logger to avoid redundant configurations.
    """
    if pid in subprocess_loggers:
        return subprocess_loggers[pid]

    log_file = os.path.join(CONFIG.path_to_logs, f"subprocess_{pid}.log")
    logger = logging.getLogger(f"subprocess_{pid}")
    logger.setLevel(logging.INFO)

    # Create file handler for logging to a process-specific log file
    file_handler = FileHandler(log_file)
    formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

    # Cache the logger for future use
    subprocess_loggers[pid] = logger
    return logger

def start(command: List[str]) -> None:
    """
    Starts a subprocess and logs its execution in the tracking file and its own log file.
    """
    try:
        # Start the subprocess
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, start_new_session=True)
        
        # Log the subprocess as running in the process tracking file
        log_process(process.pid, 'running')

        # Configure and log subprocess-specific logging
        logger = configure_subprocess_logging(process.pid)
        logger.info(f"Subprocess with PID {process.pid} started with command: {' '.join(command)}")

        typer.secho("Subprocess started. Checking status...", fg=typer.colors.BLUE)

        time.sleep(1)  # Wait to see if the process fails

        # Check if the subprocess is still running
        if process.poll() is not None:  # Process has already failed
            stderr_output = process.communicate()[1].decode('utf-8')  # Capture stderr
            logger.error(f"Subprocess with PID {process.pid} failed. Stderr: {stderr_output}")
            update_process_status(process.pid, 'failed')  # Update to 'failed' instead of '1'
            typer.secho(f"Subprocess with PID {process.pid} failed. Use 'spectre print process-log' to see error details.", fg=typer.colors.RED)
            return  # Exit early to prevent double error reporting

        typer.secho(f"Subprocess with PID {process.pid} started successfully.", fg=typer.colors.GREEN)
        logger.info(f"Subprocess with PID {process.pid} started successfully.")

    except Exception as e:
        logger = configure_subprocess_logging(process.pid)
        logger.error(f"Exception occurred in subprocess with PID {process.pid}: {str(e)}", exc_info=True)
        update_process_status(process.pid, 'failed')  # Ensure the status is 'failed' on exception
        
        # Log the exception properly
        log_process(process.pid, str(e))

        typer.secho(f"An exception occurred in subprocess with PID {process.pid}. Use 'spectre print process-log' to see error details.", fg=typer.colors.RED)
        raise typer.Exit(1)


# Stop running subprocesses and update their statuses
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

                # Update status in process tracking file
                update_process_status(pid, 'stopped')

                # Log the stop action in the subprocess log
                logger = configure_subprocess_logging(int(pid))
                logger.info(f"Subprocess with PID {pid} has been terminated.")
            except ProcessLookupError:
                typer.secho(f"Failed to terminate subprocess with PID {pid}. It may have already exited.", fg=typer.colors.RED)

    # Optionally, wipe the tracking file after stopping all processes
    wipe_process_tracking_file()
    typer.secho("All subprocesses have been addressed, and the log file has been cleared.", fg=typer.colors.GREEN)

# Log a subprocess's status in the tracking file
def log_process(pid: int, status: str) -> None:
    """Logs subprocess PID and status (running, stopped, etc.) to the tracking file."""
    subprocesses = read_from_log_file(CONFIG.path_to_processes_log)
    subprocesses[str(pid)] = status
    write_to_log_file(subprocesses, CONFIG.path_to_processes_log)

# Update a subprocess's status in the tracking file
def update_process_status(pid: int, status: str) -> None:
    """Updates the status of a specific subprocess in the tracking file."""
    subprocesses = read_from_log_file(CONFIG.path_to_processes_log)
    if str(pid) in subprocesses:
        subprocesses[str(pid)] = status
    write_to_log_file(subprocesses, CONFIG.path_to_processes_log)

# Read subprocess tracking file with default handling for missing or invalid data
def read_process_tracking_file() -> dict:
    """
    Reads the subprocess tracking file, returning a dictionary of PIDs and their statuses.
    If the file does not exist, it is created and initialized with an empty dictionary.
    """
    return read_from_log_file(CONFIG.path_to_processes_log)

# Clear the subprocess tracking file
def wipe_process_tracking_file() -> None:
    """Resets the process tracking log file to contain an empty dictionary."""
    write_to_log_file({}, CONFIG.path_to_processes_log)

# Check if any subprocess has failed
def has_failure() -> bool:
    """Checks if any subprocess has failed by looking in the tracking file."""
    subprocesses = read_from_log_file(CONFIG.path_to_processes_log)
    return any(status == 'failed' for status in subprocesses.values())
