import os
import time
import multiprocessing
from typing import List
import typer

from cfg import CONFIG
from spectre.receivers.factory import get_receiver
from spectre.watchdog.Watcher import Watcher


# Utility functions
def _calculate_total_runtime(seconds: int = 0, minutes: int = 0, hours: int = 0) -> float:
    return seconds + (minutes * 60) + (hours * 3600)


def _terminate_processes(processes: List[multiprocessing.Process]) -> None:
    for p in processes:
        if p.is_alive():
            p.terminate()
            p.join()
    typer.secho("All processes successfully terminated.", fg=typer.colors.GREEN)


def start_process(target_func, args: tuple, process_name: str) -> multiprocessing.Process:
    typer.secho(f"Starting {process_name} process ...", fg=typer.colors.BLUE)
    process = multiprocessing.Process(target=target_func, args=args, name=process_name, daemon=True)
    process.start()
    time.sleep(1)  # Allow the process to initialize

    if process.is_alive():
        typer.secho(f"{process_name.capitalize()} process started successfully", fg=typer.colors.GREEN)
    else:
        typer.secho(f"{process_name.capitalize()} process failed to start.", fg=typer.colors.RED)
        process.terminate()
    return process


def _restart_all_processes(process_infos: List[tuple]) -> List[tuple]:
    typer.secho("Restarting all processes...", fg=typer.colors.YELLOW)
    new_process_infos = []
    for process, target_func, args in process_infos:
        new_process = start_process(target_func, args, process.name)
        new_process_infos.append((new_process, target_func, args))
    return new_process_infos


def _monitor_processes(process_infos: List[tuple], total_runtime: float, force_restart: bool) -> None:
    start_time = time.time()
    typer.secho("Monitoring processes...", fg=typer.colors.BLUE)

    try:
        while time.time() - start_time < total_runtime:
            for process, _, _ in process_infos:
                if not process.is_alive():
                    typer.secho(f"Process {process.name} unexpectedly exited.", fg=typer.colors.RED)

                    if force_restart:
                        _terminate_processes([p[0] for p in process_infos])
                        process_infos = _restart_all_processes(process_infos)
                    else:
                        _terminate_processes([p[0] for p in process_infos])
                        return

            time.sleep(1)  # Poll every 1 second

        typer.secho("Session duration reached.", fg=typer.colors.GREEN)
        _terminate_processes([p[0] for p in process_infos])

    except KeyboardInterrupt:
        typer.secho("Keyboard Interrupt detected. Terminating processes.", fg=typer.colors.RED)
        _terminate_processes([p[0] for p in process_infos])


# Operation modes
def start_capture(receiver_name: str, mode: str, tags: List[str], seconds: int = 0, minutes: int = 0, hours: int = 0, force_restart: bool = False) -> None:
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)
    capture_process = start_process(_start_capture, (receiver_name, mode, tags), "capture")
    _monitor_processes([(capture_process, _start_capture, (receiver_name, mode, tags))], total_runtime, force_restart)


def start_session(receiver_name: str, mode: str, tags: List[str], force_restart: bool = False, seconds: int = 0, minutes: int = 0, hours: int = 0) -> None:
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)
    watcher_process = start_process(_start_watcher, (tags,), "watcher")
    capture_process = start_process(_start_capture, (receiver_name, mode, tags), "capture")

    if not watcher_process.is_alive() or not capture_process.is_alive():
        _terminate_processes([watcher_process, capture_process])
        return

    _monitor_processes([(watcher_process, _start_watcher, (tags,)),
                        (capture_process, _start_capture, (receiver_name, mode, tags))], total_runtime, force_restart)


# Internal process starters
def _start_capture(receiver_name: str, mode: str, tags: List[str]) -> None:
    receiver = get_receiver(receiver_name, mode=mode)
    receiver.start_capture(tags)


def _start_watcher(tags: List[str]) -> None:
    os.makedirs(CONFIG.path_to_chunks_dir, exist_ok=True)
    for tag in tags:
        watcher = Watcher(tag)
        watcher.start()
