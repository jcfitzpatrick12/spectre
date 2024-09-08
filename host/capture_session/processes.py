import psutil
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
    """
    Reads the process log from a JSON file.
    Returns an empty dictionary if the file is not found.
    """
    try:
        with open(CONFIG.path_to_processes_log, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def write_to_process_log(data: dict) -> None:
    """
    Writes the provided data dictionary to the process log.
    """
    with open(CONFIG.path_to_processes_log, 'w') as file:
        json.dump(data, file)


def update_process_log(pid: int, status: str) -> None:
    """
    Updates the process log with the current status of the process.
    """
    subprocesses = read_process_log()
    subprocesses[str(pid)] = status
    write_to_process_log(subprocesses)


def configure_subprocess_logging(pid: int) -> logging.Logger:
    """
    Configures and returns a logger for subprocesses based on the PID.
    """
    log_file = os.path.join(CONFIG.path_to_logs, f"subprocess_{pid}.log")
    logger = logging.getLogger(f"subprocess_{pid}")
    
    if not logger.handlers:  # Avoid adding multiple handlers
        file_handler = FileHandler(log_file)
        file_handler.setFormatter(Formatter('%(asctime)s:%(levelname)s:%(message)s'))
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
    
    return logger


def is_process_running(pid: int) -> bool:
    """
    Checks if a process with the given PID is still running using psutil.
    """
    try:
        process = psutil.Process(pid)
        return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:
        return False


def update_subprocess_statuses() -> None:
    """
    Updates the status of all subprocesses by reading the log file and checking their current status.
    """
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


def update_status_for_pid(pid: int, logger) -> None:
    """
    Updates the status for a subprocess based on whether it's running or stopped using psutil.
    """
    if is_process_running(pid):
        logger.info(f"The subprocess with PID {pid} is still running.")
    else:
        # Mark the process as stopped in the log
        update_process_log(pid, 'stopped')
        logger.info(f"Subprocess with PID {pid} has stopped.")


def start(command: List[str]) -> None:
    """
    Starts a subprocess with the provided command, tracks its status, and logs the result.
    """
    # Start the command as a subprocess
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    update_process_log(process.pid, 'running')
    typer.secho(f"Subprocess with PID {process.pid} started. Checking status...", fg=typer.colors.BLUE)

    # Give the subprocess time to boot up
    time.sleep(1)

    # Check if the subprocess has already exited
    if not is_process_running(process.pid):
        typer.secho(f"Subprocess with PID {process.pid} failed shortly after starting. "
                    f"Use \"spectre print process-log --pid <pid>\" to find out more.", fg=typer.colors.RED)
        update_process_log(process.pid, 'failed')
        raise typer.Exit(1)

    typer.secho(f"Subprocess with PID {process.pid} started successfully.", fg=typer.colors.GREEN)


def stop() -> None:
    """
    Stops all running subprocesses by sending a kill signal and updating their status.
    """
    subprocesses = read_process_log()

    if not subprocesses:
        typer.secho("No subprocesses found to stop.", fg=typer.colors.YELLOW)
        return

    for pid_str, status in subprocesses.items():
        pid = int(pid_str)
        logger = configure_subprocess_logging(pid)

        if status == 'running':
            try:
                # Forcefully terminate the process
                os.kill(pid, signal.SIGKILL)
                typer.secho(f"Subprocess with PID {pid} has been terminated.", fg=typer.colors.GREEN)
                logger.info(f"Subprocess with PID {pid} has been terminated.")
                update_process_log(pid, 'killed')

            except ProcessLookupError:
                typer.secho(f"Subprocess with PID {pid} was not found. It may have already exited.", fg=typer.colors.RED)

    # Clear the log after termination
    write_to_process_log({})
    typer.secho("All subprocesses have been forcefully terminated.", fg=typer.colors.GREEN)


def any_process_not_running() -> bool:
    """
    Checks if any subprocess is not running by reading the process log and evaluating their statuses.
    """
    process_log = read_process_log()
    for _, status in process_log.items():
        if status != 'running':
            return True
    return False
