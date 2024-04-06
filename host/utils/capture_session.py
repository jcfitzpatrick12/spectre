import subprocess
import os
import signal
import typer
import time

from cfg import CONFIG

def start(receiver_name: str, mode: str, tag: str):
    if is_capture_session_in_progress():
        typer.secho("A capture session is already in progress.", fg=typer.colors.RED)
        raise typer.Exit(1)

    # build the command to start the capture session
    command = [
        'python3', f'{CONFIG.path_to_start_capture}',
        '--receiver', receiver_name,
        '--tag', tag,
        '--mode', mode
    ]


    # Starting the capture subprocess
    capture_process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    update_capture_log(f"1:{capture_process.pid}")
    
    time.sleep(1)  # Wait for the subprocess to potentially fail
    if not is_capture_session_in_progress():
        typer.secho("Failed to start capture session. Check the capture log.", fg=typer.colors.RED)
        raise typer.Exit(1)
    
    typer.secho("Capture session started in the background.", fg=typer.colors.GREEN)


def stop():
    pid = get_capture_pid()
    if pid is None:
        typer.secho("No active capture session found.", fg=typer.colors.RED)
        raise typer.Exit(1)

    try:
        os.kill(pid, signal.SIGTERM)
        clear_capture_log()
        typer.secho("Capture session has been successfully terminated.", fg=typer.colors.GREEN)
    except ProcessLookupError:
        typer.secho("Failed to terminate capture session. Process may have already exited.", fg=typer.colors.RED)
        clear_capture_log()  # Ensure log is cleared even if process had already exited


def is_capture_session_in_progress():
    status = get_session_status()
    return status == 1


def get_session_status():
    try:
        with open(CONFIG.path_to_capture_log, 'r') as file:
            content = file.read().strip()
            if content.startswith('1'):
                return 1
            elif content.startswith('0'):
                return 0
            else:
                return None
            
    except FileNotFoundError:
        typer.secho(f"{CONFIG.path_to_capture_log} not found.", fg=typer.colors.RED)
        return None

def get_capture_pid():
    status = get_session_status()
    if status == 1:
        with open(CONFIG.path_to_capture_log, 'r') as file:
            content = file.read().strip()
            return int(content.split(':')[1])
    return None


def update_capture_log(content: str):
    with open(CONFIG.path_to_capture_log, 'w') as file:
        file.write(content)


def clear_capture_log():
    open(CONFIG.path_to_capture_log, "w").close()
