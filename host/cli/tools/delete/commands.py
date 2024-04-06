import typer
import os

from cli import __app_name__, __version__
from cfg import CONFIG

from spectre.capture_config.CaptureConfig import CaptureConfig
from spectre.utils import json_helpers 

app = typer.Typer()

@app.command()
def capture_config(tag: str = typer.Option(None, "--tag", "-t", help=""),
) -> None:
    
    if not tag:
        typer.secho(
            f'You must specify the tag via --tag [requested tag]',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    capture_config = CaptureConfig(tag, CONFIG.path_to_capture_configs)
    config_path = capture_config.absolute_path()

    if not os.path.exists(config_path):
        typer.secho(
            f'Could not delete capture config with tag {tag}. {config_path} does not exist.',
            fg=typer.colors.RED,
        )
    
    else:
        json_helpers.doublecheck_delete(config_path)
        os.remove(config_path)
        typer.secho(
            f'File deleted: {config_path}.',
            fg=typer.colors.YELLOW,
        )

    raise typer.Exit(1)

