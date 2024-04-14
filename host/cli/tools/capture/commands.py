import typer
import os

from cli import __app_name__, __version__
from utils import capture_session 
from cfg import CONFIG


app = typer.Typer()

@app.command()
def start(tag: str = typer.Option(..., "--tag", "-t", help="Tag for the capture session"),
          mode: str = typer.Option(..., "--mode", "-m", help="Mode for the capture"),
          receiver_name: str = typer.Option(..., "--receiver", "-r", help="Receiver name")
) -> None:
    # receiver_name is mandatory
    if not receiver_name:
        typer.secho(
            f'You must specify the receiver via --receiver [receiver name]',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    # mode is mandatory

    if not mode:
        typer.secho(
            f'You must specify the receiver mode via --mode [mode type]',
            fg=typer.colors.RED
        )
        raise typer.Exit(1)

    # tag is mandatory
    if not tag:
        typer.secho(
            f'You must specify the tag via --tag [requested tag]',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    
    if not os.path.exists(CONFIG.path_to_start_capture):
        raise FileNotFoundError(f"Could not find capture script: {CONFIG.path_to_start_capture}.")
    
    # build the command to start the capture session
    subprocess_command = [
        'python3', f'{CONFIG.path_to_start_capture}',
        '--receiver', receiver_name,
        '--tag', tag,
        '--mode', mode
    ]

    capture_session.start(subprocess_command)

@app.command()
def postproc(tag: str = typer.Option(..., "--tag", "-t", help="Tag for the capture session"),
) -> None:
    # tag is mandatory
    if not tag:
        typer.secho(
            f'You must specify the tag via --tag [requested tag]',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    if not os.path.exists(CONFIG.path_to_post_proc):
        raise FileNotFoundError(f"Could not find capture script: {CONFIG.path_to_post_proc}.")
        
    # build the command to start the capture session
    subprocess_command = [
        'python3', f'{CONFIG.path_to_post_proc}',
        '--tag', tag,
    ]
    
    print(subprocess_command)
    capture_session.start(subprocess_command)


@app.command()
def stop(
) -> None:
    capture_session.stop()

