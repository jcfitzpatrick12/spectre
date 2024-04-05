import typer
import signal
import os
import subprocess
import time

from cli import __app_name__, __version__
from cfg import CONFIG

app = typer.Typer()


@app.command()
def start(
    tag: str = typer.Option(None, "--tag", "-t", help=""),
    mode: str = typer.Option(None, "--mode", "-m", help=""),
    receiver_name: str = typer.Option(None, "--receiver", "-r", help=""),
) -> None:

    if tag is None:
        typer.secho(
        f"Tag must be specified using --tag [TAG]",
        fg=typer.colors.RED,
        )
        typer.Exit(1)
    
    if mode is None:
        typer.secho(
        f"Mode must be specified using --mode [MODE]",
        fg=typer.colors.RED,
        )
        typer.Exit(1)
    
    if receiver_name is None:
        typer.secho(
        f"Receiver name must be specified using --receiver [RECEIVER]",
        fg=typer.colors.RED,
        )
        typer.Exit(1)
        

    command = ['python3', '/home/spectre/host/utils/start_capture.py', 
            '--receiver', receiver_name, 
            '--tag', tag, 
            '--mode', mode]

    
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

    with open(CONFIG.path_to_capture_log, 'w') as capture_log:
        capture_log.write(f"1: SESSION IN PROGRESS")
    capture_log.close()
    
    typer.secho(
            f"Capture session starting ...",
            fg=typer.colors.YELLOW,
        )

    # give the capture log time to update 
    time.sleep(1)
    
    # check the logs to see if starting capture was successful.
    with open(CONFIG.path_to_capture_log, 'r') as capture_log:
        log_contents = capture_log.read()


    capture_status = int(log_contents[0])


    if capture_status == 0:
        typer.secho(
            f"Capture failed to start. Check the capture log at {CONFIG.path_to_capture_log}",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    else:   
        # the capture was a success, so capture the PID and inform the user success
        with open(CONFIG.path_to_PID, 'w') as file:
            file.write(str(process.pid))

        typer.secho(
                f"Capture session has succesfully started.",
                fg=typer.colors.GREEN,
            )
        return


@app.command()
def stop(
) -> None:
    try:
        # find the pid of the capture subprocess
        with open(CONFIG.path_to_PID, 'r') as file:
            pid = int(file.read().strip())
            
        # Kill the process
        os.kill(pid, signal.SIGTERM)
        typer.secho(
            f"Capture session has been successfully terminated.",
            fg=typer.colors.GREEN,
        )

        # clear the capture log
        open(CONFIG.path_to_capture_log, "w").close()

    except FileNotFoundError:
        typer.secho(
            f"Error: The PID file does not exist.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    except ProcessLookupError:
        typer.secho(
            f"Error: The process does not exist or has already been terminated.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    return