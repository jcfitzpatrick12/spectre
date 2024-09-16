# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
import os

from host.cli import __app_name__, __version__

from spectre.file_handlers.json.FitsConfigHandler import FitsConfigHandler
from spectre.file_handlers.json.CaptureConfigHandler import CaptureConfigHandler
from spectre.file_handlers.chunks.Chunks import Chunks

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
    
    for chunk in chunks:
        if suppress_doublecheck:
            doublecheck_delete = False
        else:
            doublecheck_delete = True
        if chunk.has_file(ext):
            chunk.delete_file(ext, doublecheck_delete=doublecheck_delete)
            typer.secho(f"File deleted: {chunk.get_file(ext).file_path}.", fg=typer.colors.YELLOW)
    
    typer.Exit()


@app.command()
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
) -> None:
    fits_config_handler = FitsConfigHandler(tag)
    fits_config_handler.delete()

    typer.secho(
            f'File deleted: {fits_config_handler.get_path()}.',
            fg=typer.colors.YELLOW,
        )
    raise typer.Exit()


@app.command()
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
) -> None:

    capture_config_handler = CaptureConfigHandler(tag)
    capture_config_handler.delete()

    typer.secho(
            f'File deleted: {capture_config_handler.get_path()}.',
            fg=typer.colors.YELLOW,
        )
    raise typer.Exit()





