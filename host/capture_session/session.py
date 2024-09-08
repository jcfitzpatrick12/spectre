from typing import List
import time
import logging
import os
import typer

from cfg import CONFIG
from spectre.receivers.factory import get_receiver
from spectre.watchdog.Watcher import Watcher
from host.capture_session.processes import (
    update_process_log,
    start,
    any_process_not_running,
    update_subprocess_statuses,
    stop
)


def start_capture(receiver_name: str,
                  mode: str,
                  tags: List[str],
                  run_as_foreground_ps: bool = False) -> None:
    if not os.path.exists(CONFIG.path_to_start_capture):
        raise FileNotFoundError(f"Could not find capture script: {CONFIG.path_to_start_capture}.")
    
    if run_as_foreground_ps:
        receiver = get_receiver(receiver_name, mode=mode)
        receiver.start_capture(tags)
    else:
        # Build the command to start the capture session
        subprocess_command = [
            'python3', f'{CONFIG.path_to_start_capture}',
            '--receiver', receiver_name,
            '--mode', mode
        ]

        subprocess_command += ['--tag']
        for tag in tags:
            subprocess_command += [tag]

        start(subprocess_command)
    return


def start_watcher(tags: List[str],
                  run_as_foreground_ps: bool = False) -> None:
    if not os.path.exists(CONFIG.path_to_start_watcher):
        raise FileNotFoundError(f"Could not find watcher script: {CONFIG.path_to_start_watcher}.")
    
    if run_as_foreground_ps:
        if not os.path.exists(CONFIG.path_to_chunks_dir):
            os.mkdir(CONFIG.path_to_chunks_dir)
        for tag in tags:
            watcher = Watcher(tag)
            watcher.start()
    else:
        for tag in tags:
            # Build the command to start the watcher
            subprocess_command = [
                'python3', f'{CONFIG.path_to_start_watcher}',
                '--tag', tag,
            ]
            start(subprocess_command)
    return


def start_session(receiver_name: str,
                  mode: str,
                  tags: List[str],
                  force_restart: bool = False) -> None:
    
    start_watcher(tags)
    start_capture(receiver_name, mode, tags)

    typer.secho("Periodically checking subprocess statuses ...")
    # Polling loop to check for stopped processes
    while True:
        time.sleep(5)  # Sleep to reduce CPU usage
        # Update the status of all subprocesses
        update_subprocess_statuses()
        # If any subprocess is not running, restart or exit depending on the flag
        if any_process_not_running():
            typer.secho("A subprocess has exited unexpectedly.", fg=typer.colors.RED)
            
            if force_restart:
                typer.secho("Restarting session due to stopped process.", fg = typer.colors.YELLOW)
                stop()
                start_session(receiver_name, mode, tags, force_restart = force_restart)
                return  # Exit the current loop and function, new session will take over
            else:
                typer.secho("Stopping session as processes are not running.", fg = typer.colors.YELLOW)
                break
    
    # Stop all subprocesses
    stop()
    typer.secho("Session stopped.", fg = typer.colors.GREEN)
