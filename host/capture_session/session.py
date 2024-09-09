from typing import List
import time
import os
import multiprocessing

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
    """Gracefully terminate all running processes."""
    for p in processes:
        if p.is_alive():
            p.terminate()
            p.join()


def start_session(receiver_name: str,
                  mode: str,
                  tags: List[str],
                  force_restart: bool = False,
                  seconds: int = 0,
                  minutes: int = 0,
                  hours: int = 0) -> None:

    # Calculate total runtime in seconds
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)

    # Create and start the processes
    watcher_process = multiprocessing.Process(target=start_watcher, args=(tags,), name="Watcher")
    capture_process = multiprocessing.Process(target=start_capture, args=(receiver_name, mode, tags), name="Capture")
    
    # Start processes
    watcher_process.start()
    capture_process.start()

    # Check for boot-up success within the first second
    time.sleep(1)  # Allow processes to "boot up"
    
    if not watcher_process.is_alive():
        print("Watcher process failed to start. Terminating session.")
        _terminate_processes([watcher_process, capture_process])
        return

    if not capture_process.is_alive():
        print("Capture process failed to start. Terminating session.")
        _terminate_processes([watcher_process, capture_process])
        return

    # Monitor both processes
    try:
        _monitor_processes([watcher_process, capture_process], total_runtime, force_restart, receiver_name, mode, tags)
    except KeyboardInterrupt:
        print("Keyboard Interrupt detected. Terminating all processes.")
        _terminate_processes([watcher_process, capture_process])
