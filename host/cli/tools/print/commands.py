import typer
import os

from cli import __app_name__, __version__
from cfg import CONFIG

from spectre.capture_config.CaptureConfig import CaptureConfig

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


    try:
        capture_config = CaptureConfig(tag, CONFIG.path_to_capture_configs)
        config_dict = capture_config.load_as_dict()
        for key, value in config_dict.items():
            typer.secho(
                f"{key}: {value}"
            )

    except Exception as e:
        typer.secho(
            f'Could not print capture-config. Received: {e}',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    