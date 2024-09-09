from typing import List
import time
import os
import multiprocessing
import typer

from cfg import CONFIG
from spectre.receivers.factory import get_receiver
from spectre.watchdog.Watcher import Watcher

def start_capture(receiver_name: str, 
                  mode: str, 
                  tags: List[str]) -> None:
    receiver = get_receiver(receiver_name, mode=mode)
    receiver.start_capture(tags)
    return

def start_watcher(tags: List[str]) -> None:
    if not os.path.exists(CONFIG.path_to_chunks_dir):
        os.mkdir(CONFIG.path_to_chunks_dir)
    for tag in tags:
        watcher = Watcher(tag)
        watcher.start()
    return

def _calculate_total_runtime(seconds: int = 0,
                            minutes: int = 0, 
                            hours: int = 0) -> float:
    return seconds + (minutes * 60) + (hours * 3600)

def _monitor_processes(processes: List[multiprocessing.Process], 
                      total_runtime: float, 
                      force_restart: bool, 
                      receiver_name: str, 
                      mode: str, 
                      tags: List[str]) -> None:
    start_time = time.time()
    
    while True:
        elapsed_time = time.time() - start_time

        # Terminate processes when total runtime is reached
        if elapsed_time >= total_runtime:
            print("Session duration reached. Terminating all processes.")
            _terminate_processes(processes)
            return

        # Check if any process has stopped
        for p in processes:
            if not p.is_alive():
                if force_restart:
                    print(f"Process {p.name} stopped. Restarting session...")
                    _terminate_processes(processes)
                    start_session(receiver_name, mode, tags, force_restart=force_restart)
                    return
                else:
                    print(f"Process {p.name} stopped. Terminating session.")
                    _terminate_processes(processes)
                    return

        time.sleep(5)  # Poll every 5 seconds

def _terminate_processes(processes: List[multiprocessing.Process]) -> None:
    for p in processes:
        if p.is_alive():
            p.terminate()
            p.join()

def _start_process(target_func, args: tuple, process_name: str) -> multiprocessing.Process:
    typer.secho(f"Starting {process_name} process ...", fg=typer.colors.BLUE)
    process = multiprocessing.Process(target=target_func, args=args, name=process_name, daemon=True)
    process.start()

    # Give the process a second to "boot up"
    time.sleep(1)

    if process.is_alive():
        typer.secho(f"{process_name.capitalize()} process booted up successfully", fg=typer.colors.GREEN)
    else:
        print(f"{process_name.capitalize()} process failed to start.")
        process.terminate()  # Terminate if it failed to start
    return process

def start_session(receiver_name: str,
                  mode: str,
                  tags: List[str],
                  force_restart: bool = False,
                  seconds: int = 0,
                  minutes: int = 0,
                  hours: int = 0) -> None:

    # Calculate total runtime in seconds
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)

    # Start watcher process using the helper function
    watcher_process = _start_process(target_func=start_watcher, 
                                     args=(tags,), 
                                     process_name="watcher")

    # If the watcher process failed to start, terminate and return
    if not watcher_process.is_alive():
        _terminate_processes([watcher_process])
        return

    # Start capture process using the helper function
    capture_process = _start_process(target_func=start_capture, 
                                     args=(receiver_name, mode, tags), 
                                     process_name="capture")

    # If the capture process failed to start, terminate both processes and return
    if not capture_process.is_alive():
        _terminate_processes([watcher_process, capture_process])
        return

    # Monitor both processes
    try:
        _monitor_processes([watcher_process, capture_process], total_runtime, force_restart, receiver_name, mode, tags)
    except KeyboardInterrupt:
        print("Keyboard Interrupt detected. Terminating all processes.")
        _terminate_processes([watcher_process, capture_process])
