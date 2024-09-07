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



def configure_subprocess_logging(pid: int) -> logging.Logger:
    """
    Configures and returns a logger for the subprocess, with a log file named after the process PID.
    """
    log_file = os.path.join(CONFIG.path_to_logs, f"subprocess_{pid}.log")
    logger = logging.getLogger(f"subprocess_{pid}")
    logger.setLevel(logging.INFO)

    # Create file handler for logging to a process-specific log file
    file_handler = FileHandler(log_file)
    formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)
    return logger


def start(command: List[str]) -> None:
    """
    Starts a subprocess and logs its execution in the tracking file and its own log file.
    """
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    
    # Log the subprocess as running in the process tracking file
    log_process(process.pid, 'running')  # Log the process as running

    # Configure and log subprocess specific logging
    logger = configure_subprocess_logging(process.pid)
    logger.info(f"Subprocess with PID {process.pid} started with command: {' '.join(command)}")

    typer.secho("Subprocess started. Checking status...", fg=typer.colors.BLUE)

    time.sleep(1)  # Wait to see if the process fails

    if process.poll() is not None:  # If the process fails
        typer.secho(f"Subprocess with PID {process.pid} failed. Check the log for details.", fg=typer.colors.RED)
        logger.error(f"Subprocess with PID {process.pid} failed.")
        update_process_status(process.pid, 'failed')
        raise typer.Exit(1)
    else:
        typer.secho(f"Subprocess with PID {process.pid} started successfully.", fg=typer.colors.GREEN)
        logger.info(f"Subprocess with PID {process.pid} started successfully.")


def stop() -> None:
    """
    Stops all running subprocesses listed in the process tracking file.
    """
    subprocesses = read_process_tracking_file()
    
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


def log_process(pid: int, status: str) -> None:
    """
    Logs subprocess PID and status (running, stopped, etc.) to the tracking file.
    """
    subprocesses = read_process_tracking_file()
    subprocesses[str(pid)] = status
    with open(CONFIG.path_to_processes_log, 'w') as file:
        json.dump(subprocesses, file)


def update_process_status(pid: int, status: str) -> None:
    """
    Updates the status of a specific subprocess in the tracking file.
    """
    subprocesses = read_process_tracking_file()
    if str(pid) in subprocesses:
        subprocesses[str(pid)] = status
    with open(CONFIG.path_to_processes_log, 'w') as file:
        json.dump(subprocesses, file)


def read_process_tracking_file() -> dict:
    """
    Reads the subprocess tracking file, returning a dictionary of PIDs and their statuses.
    If the file does not exist, it is created and initialized with an empty dictionary.
    """
    try:
        with open(CONFIG.path_to_processes_log, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # If the file does not exist, create it and initialize with an empty dictionary
        typer.secho(f"{CONFIG.path_to_processes_log} not found. Creating and initializing with an empty dictionary.", fg=typer.colors.YELLOW)
        with open(CONFIG.path_to_processes_log, 'w') as file:
            json.dump({}, file)  # Initialize with an empty dictionary
        return {}
    except json.JSONDecodeError:
        # If the file contains invalid JSON, warn and reset it to an empty dictionary
        typer.secho(f"Invalid JSON in {CONFIG.path_to_processes_log}. Initializing with an empty dictionary.", fg=typer.colors.RED)
        with open(CONFIG.path_to_processes_log, 'w') as file:
            json.dump({}, file)
        return {}


def wipe_process_tracking_file() -> None:
    """
    Resets the process tracking log file to contain an empty dictionary.
    """
    with open(CONFIG.path_to_processes_log, 'w') as file:
        json.dump({}, file)


def has_failure() -> bool:
    """
    Checks if any subprocess has failed by looking in the tracking file.
    """
    subprocesses = read_process_tracking_file()
    return any(status == 'failed' for status in subprocesses.values())
