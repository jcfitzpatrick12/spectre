import subprocess
import json
import os
import signal
import time
import typer
from typing import List

from cfg import CONFIG

def start(command: List[str]) -> None:

    # start the subprocess
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    # and log that the subprocess is currently running
    log_subprocess(process.pid, '1')  # '1' indicates the process is running

    typer.secho("Subprocess started. Checking status...", fg=typer.colors.BLUE)

    # Wait a bit to see if the process fails
    time.sleep(1)
    
    # Check if the started process is still running
    if not process.poll() is None:
        typer.secho(f"Subprocess with PID {process.pid} failed shortly after starting. Check the log for more details.", fg=typer.colors.RED)
        raise typer.Exit(1)
    else:
        typer.secho(f"Subprocess with PID {process.pid} started successfully.", fg=typer.colors.GREEN)


def stop() -> None:
    """
    Stops all subprocesses listed in the log file with status '1',
    and completely wipes the process.pid log.
    """
    subprocesses = read_log()
    if not subprocesses:
        typer.secho("No subprocesses found to stop.", fg=typer.colors.YELLOW)
        return

    for pid, status in subprocesses.items():
        if status == '1':
            try:
                os.kill(int(pid), signal.SIGTERM)
                typer.secho(f"Subprocess with PID {pid} has been successfully terminated.", fg=typer.colors.GREEN)
            except ProcessLookupError:
                typer.secho(f"Failed to terminate subprocess with PID {pid}. Process may have already exited.", fg=typer.colors.RED)

    # After attempting to stop all processes, wipe the log file completely
    wipe_log()
    typer.secho("All subprocesses have been addressed, and the log file has been cleared.", fg=typer.colors.GREEN)

def wipe_log() -> None:
    """
    Resets the process.pid log file to contain an empty dictionary.
    """
    with open(CONFIG.path_to_capture_log, 'w') as file:
        json.dump({}, file)

def has_failure() -> bool:
    """
    Checks if any subprocess has failed.
    """
    subprocesses = read_log()
    return any(status.startswith(0) for status in subprocesses.values())


def log_subprocess(pid: int, status: str) -> None:
    """
    Logs subprocess PID and status to the log file.
    """
    subprocesses = read_log()
    subprocesses[str(pid)] = status
    with open(CONFIG.path_to_capture_log, 'w') as file:
        json.dump(subprocesses, file)

def read_log() -> dict:
    """
    Reads the subprocess log, returning a dictionary of PIDs to statuses.
    If the file does not exist, it is created and initialized with an empty dictionary.
    """
    try:
        with open(CONFIG.path_to_capture_log, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # If the file does not exist, create it and initialize with an empty dictionary
        typer.secho(f"{CONFIG.path_to_capture_log} not found. Creating and initializing with an empty dictionary.", fg=typer.colors.YELLOW)
        with open(CONFIG.path_to_capture_log, 'w') as file:
            json.dump({}, file)  # Initialize the file with an empty dictionary
        return {}
    except json.JSONDecodeError:
        # If the file contains invalid JSON, warn and return an empty dictionary
        typer.secho(f"Invalid JSON in {CONFIG.path_to_capture_log}. Initializing with an empty dictionary.", fg=typer.colors.RED)
        with open(CONFIG.path_to_capture_log, 'w') as file:
            json.dump({}, file)
        return {}

