import typer
import os

from host.cli import __app_name__, __version__
from cfg import CONFIG

from spectre.json_config.CaptureConfigHandler import CaptureConfigHandler
from spectre.json_config.FitsConfigHandler import FitsConfigHandler
from spectre.chunks.Chunks import Chunks

app = typer.Typer()

@app.command()
def chunks(tag: str = typer.Option(..., "--tag", "-t", help=""),
           ext: str = typer.Option(..., "--ext", "-e", help=""),
           year: int = typer.Option(..., "--year", "-y", help=""),
           month: int = typer.Option(..., "--month", "-m", help=""),
           day: int = typer.Option(..., "--day", "-d", help=""),
           suppress_doublecheck: bool = typer.Option(False, "--suppress-doublecheck", help="")
) -> None:
    chunks = Chunks(tag, 
                year=year, 
                month=month,
                day=day)
    for chunk in chunks.dict.values():
        # Use getattr to dynamically get the attribute based on 'ext'
        attribute = getattr(chunk, ext, None)
        if attribute is None:
            typer.echo(f"No attribute '{ext}' found on chunk")
            continue

        if suppress_doublecheck:
            doublecheck_delete = False
        else:
            doublecheck_delete = True
        # Assuming the attribute itself is an object that has a 'delete_self' method
        attribute.delete_self(doublecheck_delete=doublecheck_delete)
    typer.Exit()

@app.command()
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
) -> None:
    fits_config_handler = FitsConfigHandler(tag)
    fits_config_handler.delete_self()

    typer.secho(
            f'File deleted: {fits_config_handler.absolute_path()}.',
            fg=typer.colors.YELLOW,
        )
    raise typer.Exit()


@app.command()
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
) -> None:

    capture_config_handler = CaptureConfigHandler(tag)
    capture_config_handler.delete_self()

    typer.secho(
            f'File deleted: {capture_config_handler.absolute_path()}.',
            fg=typer.colors.YELLOW,
        )
    
    raise typer.Exit()





