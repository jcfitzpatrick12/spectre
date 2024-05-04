import typer
import os
from typing import List

from host.cli import __app_name__, __version__
from host.utils import capture_session 
from cfg import CONFIG


app = typer.Typer()

@app.command()
def start(receiver_name: str = typer.Option(..., "--receiver", "-r", help="Specify the receiver name"),
          mode: str = typer.Option(..., "--mode", "-m", help="Specify the mode for capture"),
          tags: List[str] = typer.Option(..., "--tag", "-t", help="Specify the tags for the capture session."),
) -> None:

    if not os.path.exists(CONFIG.path_to_start_capture):
        raise FileNotFoundError(f"Could not find capture script: {CONFIG.path_to_start_capture}.")
    

    # build the command to start the capture session
    subprocess_command = [
        'python3', f'{CONFIG.path_to_start_capture}',
        '--receiver', receiver_name,
        '--mode', mode
    ]

    subprocess_command += ['--tag']
    for tag in tags:
        subprocess_command += [tag]

    capture_session.start(subprocess_command)

@app.command()
def start_watcher(tag: str = typer.Option(..., "--tag", "-t", help="Tag for the capture session"),
) -> None:
    
    if not os.path.exists(CONFIG.path_to_start_watcher):
        raise FileNotFoundError(f"Could not find capture script: {CONFIG.path_to_start_watcher}.")
        
    # build the command to start the capture session
    subprocess_command = [
        'python3', f'{CONFIG.path_to_start_watcher}',
        '--tag', tag,
    ]
    
    capture_session.start(subprocess_command)


@app.command()
def stop(
) -> None:
    capture_session.stop()

