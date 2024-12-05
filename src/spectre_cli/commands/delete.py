# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer

from spectre_cli.commands import safe_request
from spectre_cli.commands import (
    TAG_HELP,
    PROCESS_TYPE_HELP,
    DAY_HELP,
    MONTH_HELP,
    YEAR_HELP,
    EXTENSIONS_HELP
)

delete_app = typer.Typer()

def _secho_deleted_files(file_names: list[str]
) -> None:
    if not file_names:
        typer.secho(f"No files found", fg="yellow")
        return 
    
    for file_name in file_names:
        typer.secho(f"Deleted '{file_name}'", fg = "yellow")


def _secho_deleted_file(file_name: str
) -> None:
    typer.secho(f"Deleted '{file_name}'", fg = "yellow")


@delete_app.command()
def logs(
    process_type: str = typer.Option(None, "--process-type", help=PROCESS_TYPE_HELP),
    year: int = typer.Option(None, "--year", "-y", help=YEAR_HELP),
    month: int = typer.Option(None, "--month", "-m", help=MONTH_HELP),
    day: int = typer.Option(None, "--day", "-d", help=DAY_HELP),
) -> None:
    payload = {
        "process_type": process_type,
        "year": year,
        "month": month,
        "day": day
    }
    jsend_dict = safe_request("delete/logs", "DELETE", payload)
    file_names = jsend_dict["data"]
    _secho_deleted_files(file_names)
    raise typer.Exit()


@delete_app.command()
def chunk_files(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
                extensions: list[str] = typer.Option(..., "--extension", "-e", help=EXTENSIONS_HELP),
                year: int = typer.Option(None, "--year", "-y", help=YEAR_HELP),
                month: int = typer.Option(None, "--month", "-m", help=MONTH_HELP),
                day: int = typer.Option(None, "--day", "-d", help=DAY_HELP),
) -> None:
    payload = {
        "tag": tag,
        "extensions": extensions,
        "year": year,
        "month": month,
        "day": day
    }
    jsend_dict = safe_request("delete/chunk-files", 
                              "DELETE", 
                              payload)
    file_names = jsend_dict["data"]
    _secho_deleted_files(file_names)
    raise typer.Exit()


@delete_app.command()
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
) -> None:
    payload = {
        "tag": tag
    }
    jsend_dict = safe_request("delete/fits-config", 
                              "DELETE", 
                              payload)
    file_name = jsend_dict["data"]
    _secho_deleted_file(file_name)
    raise typer.Exit()


@delete_app.command()
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
) -> None:
    payload = {
        "tag": tag
    }
    jsend_dict = safe_request("delete/capture-config",
                              "DELETE",
                              payload)
    file_name = jsend_dict["data"]
    _secho_deleted_file(file_name)
    raise typer.Exit()





