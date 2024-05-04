import typer
import os

from host.cli import __app_name__, __version__
from cfg import CONFIG

from spectre.json_config.CaptureConfigHandler import CaptureConfigHandler
from spectre.json_config.FitsConfigHandler import FitsConfigHandler
from spectre.utils import json_helpers

app = typer.Typer()

@app.command()
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
) -> None:

    # try:
    fits_config_handler = FitsConfigHandler(tag)
    json_helpers.delete_json_config(fits_config_handler, "fits_config")

    # except Exception as e:
    #     typer.secho(
    #         f'Creating fits config failed: {e}',
    #         fg=typer.colors.RED,
    #     )
    #     raise typer.Exit(1)


    typer.secho(
            f'File deleted: {fits_config_handler.absolute_path()}.',
            fg=typer.colors.YELLOW,
        )


@app.command()
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
) -> None:

    # try:
    capture_config_handler = CaptureConfigHandler(tag)
    json_helpers.delete_json_config(capture_config_handler, "capture_config")

    # except Exception as e:
    #     typer.secho(
    #         f'Creating capture config failed: {e}',
    #         fg=typer.colors.RED,
    #     )
    #     raise typer.Exit(1)


    typer.secho(
            f'File deleted: {capture_config_handler.absolute_path()}.',
            fg=typer.colors.YELLOW,
        )





