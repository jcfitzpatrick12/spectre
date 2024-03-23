import typer
import os

from cli import __app_name__, __version__
from cli.cfg import CONFIG

from cli.cfg.CaptureConfig import CaptureConfig
# from cli.json_config.GlobalConfig import GlobalConfig
# from cli.capture.config.defined_params import defined_params 
# from spectre.capture.config import action

app = typer.Typer()
            

@app.command()
def capture_config(
    tag: str = typer.Option(None, "--tag", "-t", help=""),
) -> None:
    

    if not tag:
        typer.secho(
            f'You must specify the tag via --tag [requested tag]',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)


    try:
        capture_config = CaptureConfig(tag)
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
    