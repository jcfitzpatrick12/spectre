import typer
import os

from cli import __app_name__, __version__
from cfg import CONFIG

app = typer.Typer()

@app.command()
def capture_configs(
) -> None:
    json_config_files = os.listdir(CONFIG.json_configs_dir)
    typer.secho(f'Listing all capture configs in the directory: {CONFIG.json_configs_dir}')
    for json_config_file in json_config_files:
        if json_config_file.startswith("capture_config"):
            typer.secho(
                f'-> {json_config_file}',
            )
    raise typer.Exit(1)


@app.command()
def tags(
) -> None:
    # if len(capture_config_files) == 0:
    typer.secho(f'Listing all defined tags.')
    json_config_files = os.listdir(CONFIG.json_configs_dir)
    for json_config_file in json_config_files:
        if json_config_file.startswith("capture_config"):
            config_file_name = os.path.splitext(json_config_file)[0]
            tag = "_".join(config_file_name.split("_")[2:])
            typer.secho(
                f'-> {tag}',
            )
    raise typer.Exit(1)

