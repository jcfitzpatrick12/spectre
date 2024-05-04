import typer
import os

from host.cli import __app_name__, __version__
from cfg import CONFIG

from spectre.json_config.CaptureConfigHandler import CaptureConfigHandler
from spectre.json_config.FitsConfigHandler import FitsConfigHandler
# from spectre.json_config.TagMap import TagMap

app = typer.Typer()

@app.command()
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
) -> None:


    try:
        fits_config_handler = FitsConfigHandler(tag)
        config_dict = fits_config_handler.load_as_dict()
        for key, value in config_dict.items():
            typer.secho(
                f"{key}: {value}"
            )

    except Exception as e:
        typer.secho(
            f'Could not print fits config. Received: {e}',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

@app.command()
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
) -> None:


    try:
        capture_config_handler = CaptureConfigHandler(tag)
        config_dict = capture_config_handler.load_as_dict()
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
    
