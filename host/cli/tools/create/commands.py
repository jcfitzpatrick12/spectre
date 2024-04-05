import typer
from typing import List

from cli import __app_name__, __version__
from cfg import CONFIG
from spectre.receivers.Receiver import Receiver


app = typer.Typer()

@app.command()
def capture_config(
    tag: str = typer.Option(None, "--tag", "-t", help=""),
    mode: str = typer.Option(None, "--mode", "-m", help=""),
    receiver_name: str = typer.Option(None, "--receiver", "-r", help=""),
    params: List[str] = typer.Option([], "--param", "-p", help="Pass arbitrary key-value pairs.", metavar="KEY=VALUE")
) -> None:
    
    # tag is mandatory
    if not tag:
        typer.secho(
            f'You must specify the tag via --tag [requested tag]',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
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
    
    
    # # # # #save the params to file as a validated configuration file
    try:
    # # instantiate the receiver specific capture config class 
        receiver = Receiver(receiver_name)
        receiver.set_mode(mode)
        receiver.save_params_as_capture_config(params, tag, CONFIG.path_to_capture_configs)

    except Exception as e:
        typer.secho(
            f'Creating capture config failed: {e}',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    typer.secho(f"The capture config for tag \"{tag}\" has been created.", fg=typer.colors.GREEN)
    

