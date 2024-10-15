# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
import os

from host.cli import __app_name__, __version__

from spectre.logging import LogHandlers
from spectre.file_handlers.json.handlers import (
    FitsConfigHandler,
    CaptureConfigHandler
)
from spectre.chunks import Chunks

app = typer.Typer()

@app.command()
def logs(
    process_type: str = typer.Option(None, "--process-type", help="Filter logs by process type"),
    year: int = typer.Option(None, "--year", "-y", help="Specify year for logs"),
    month: int = typer.Option(None, "--month", "-m", help="Specify month for logs"),
    day: int = typer.Option(None, "--day", "-d", help="Specify day for logs"),
    suppress_doublecheck: bool = typer.Option(False, "--suppress-doublecheck", help="")
) -> None:
    log_handlers = LogHandlers(process_type,
                               year,
                               month,
                               day)
    for log_handler in log_handlers:
        # if process type is specified, disregard all logs of differing process types
        if process_type and log_handler.process_type != process_type:
            continue
        if suppress_doublecheck:
            doublecheck_delete = False
        else:
            doublecheck_delete = True
        log_handler.delete(doublecheck_delete=doublecheck_delete)
        typer.secho(f"File deleted: {log_handler.file_path}.", fg=typer.colors.YELLOW)

@app.command()
def chunks(tag: str = typer.Option(..., "--tag", "-t", help=""),
           extensions: list[str] = typer.Option(..., "--extension", "-e", help=""),
           year: int = typer.Option(None, "--year", "-y", help=""),
           month: int = typer.Option(None, "--month", "-m", help=""),
           day: int = typer.Option(None, "--day", "-d", help=""),
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
        for extension in extensions:
            if chunk.has_file(extension):
                chunk.delete_file(extension, doublecheck_delete=doublecheck_delete)
                typer.secho(f"File deleted: {chunk.get_file(extension).file_path}.", fg=typer.colors.YELLOW)
    
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





