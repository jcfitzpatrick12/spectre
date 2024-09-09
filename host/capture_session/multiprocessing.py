import os
import time
import multiprocessing
from typing import List
import typer

from cfg import CONFIG
from spectre.receivers.factory import get_receiver
from spectre.watchdog.Watcher import Watcher


# Utility functions for common tasks
def _calculate_total_runtime(seconds: int = 0, minutes: int = 0, hours: int = 0) -> float:
    return seconds + (minutes * 60) + (hours * 3600)


def _terminate_processes(processes: List[multiprocessing.Process]) -> None:
    for p in processes:
        if p.is_alive():
            p.terminate()
            p.join()
    typer.secho(f"All processes successfully terminated.", fg=typer.colors.GREEN)


def start_process(target_func, args: tuple, process_name: str) -> multiprocessing.Process:
    typer.secho(f"Starting {process_name} process ...", fg=typer.colors.BLUE)
    process = multiprocessing.Process(target=target_func, args=args, name=process_name, daemon=True)
    process.start()

    # Allow the process to "boot up"
    time.sleep(1)

    if process.is_alive():
        typer.secho(f"{process_name.capitalize()} process started successfully", fg=typer.colors.GREEN)
    else:
        typer.secho(f"{process_name.capitalize()} process failed to start.", fg=typer.colors.RED)
        process.terminate()
    return process


def _restart_process(process_name: str, target_func, args: tuple) -> multiprocessing.Process:
    typer.secho(f"Restarting {process_name} process ...", fg=typer.colors.YELLOW)
    return start_process(target_func, args, process_name)


# Shared monitoring logic for any set of processes
def _monitor_processes(processes: List[multiprocessing.Process], total_runtime: float, force_restart: bool) -> None:
    message = "Monitoring process ..." if len(processes) == 1 else "Monitoring processes ..."
    typer.secho(message, fg=typer.colors.BLUE)
    start_time = time.time()

    try:
        while True:
            elapsed_time = time.time() - start_time

            # Terminate when the total runtime is reached
            if elapsed_time >= total_runtime:
                typer.secho("Session duration reached.", fg=typer.colors.GREEN)
                _terminate_processes(processes)
                return

            # Monitor each process
            for i, p in enumerate(processes):
                if not p.is_alive():
                    typer.secho(f"Process {p.name} unexpectedly exited.", fg=typer.colors.RED)
                    
                    if force_restart:
                        typer.secho(f"Force restarting process {p.name}...", fg=typer.colors.YELLOW)
                        processes[i] = _restart_process(p.name, p._target, p._args)
                    else:
                        _terminate_processes(processes)
                        return

            time.sleep(5)  # Poll every 5 seconds
    except KeyboardInterrupt:
        typer.secho("Keyboard Interrupt detected. Terminating processes.", fg=typer.colors.RED)
        _terminate_processes(processes)


# Separate functions for each operation mode
def start_capture(receiver_name: str, mode: str, tags: List[str], 
                  seconds: int = 0, minutes: int = 0, hours: int = 0, force_restart: bool = False) -> None:
    # Calculate total runtime in seconds
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)

    # Start capture process using the helper function
    capture_process = start_process(target_func=_start_capture, args=(receiver_name, mode, tags), process_name="capture")

    # Monitor the capture process
    _monitor_processes([capture_process], total_runtime, force_restart)


def start_session(receiver_name: str, mode: str, tags: List[str], 
                  force_restart: bool = False, seconds: int = 0, minutes: int = 0, hours: int = 0) -> None:
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)

    # Start the watcher and capture processes
    watcher_process = start_process(target_func=_start_watcher, args=(tags,), process_name="watcher")
    capture_process = start_process(target_func=_start_capture, args=(receiver_name, mode, tags), process_name="capture")

    # If any process fails to start, terminate both
    if not watcher_process.is_alive() or not capture_process.is_alive():
        _terminate_processes([watcher_process, capture_process])
        return

    # Monitor both processes
    _monitor_processes([watcher_process, capture_process], total_runtime, force_restart)


# Functions that can be mapped to CLI commands
def _start_capture(receiver_name: str, mode: str, tags: List[str]) -> None:
    receiver = get_receiver(receiver_name, mode=mode)
    receiver.start_capture(tags)


def _start_watcher(tags: List[str]) -> None:
    if not os.path.exists(CONFIG.path_to_chunks_dir):
        os.mkdir(CONFIG.path_to_chunks_dir)
    for tag in tags:
        watcher = Watcher(tag)
        watcher.start()
