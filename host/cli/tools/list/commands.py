import typer
import os

from cli import __app_name__, __version__
from cli.cfg import CONFIG

app = typer.Typer()

@app.command()
def capture_configs(
) -> None:
    capture_config_files = os.listdir(CONFIG.path_to_capture_configs)
    typer.secho(f'Listing all capture configs in the directory: {CONFIG.path_to_capture_configs}')
    for capture_config_file in capture_config_files:
        typer.secho(
            f'-> {capture_config_file}',
        )
    raise typer.Exit(1)


@app.command()
def tags(
) -> None:
    
    capture_config_files = os.listdir(CONFIG.path_to_capture_configs)

    # if len(capture_config_files) == 0:
    typer.secho(f'Listing all defined tags.')
    for capture_config_file in capture_config_files:
        config_file_name = os.path.splitext(capture_config_file)[0]
        tag = "_".join(config_file_name.split("_")[2:])
        typer.secho(
            f'-> {tag}',
        )
    raise typer.Exit(1)
