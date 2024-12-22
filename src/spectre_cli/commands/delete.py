# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer

from spectre_cli.commands import safe_request
from spectre_cli.commands import CliHelp

delete_app = typer.Typer(
    help = "Delete resources."
)

def _secho_deleted_files(file_names: list[str]) -> None:
    if not file_names:
        typer.secho(f"No files found", fg="yellow")
        return 
    
    for file_name in file_names:
        typer.secho(f"Deleted '{file_name}'", fg="yellow")


def _secho_deleted_file(file_name: str) -> None:
    typer.secho(f"Deleted '{file_name}'", fg="yellow")


def _caution_irreversible(force: bool) -> None:
    if force:
        return
    typer.secho("This action is irreversible. Do you wish to continue? [y/n]", fg="red", bold=True)
    confirmation = input().strip().lower()
    if confirmation not in ("y", "yes"):
        typer.secho("Operation cancelled.", fg="yellow")
        raise typer.Exit()


@delete_app.command(
        help = ("Delete log files.")
)
def logs(
    process_type: str = typer.Option(None, "--process-type", help=CliHelp.PROCESS_TYPE),
    year: int = typer.Option(None, "--year", "-y", help=CliHelp.YEAR),
    month: int = typer.Option(None, "--month", "-m", help=CliHelp.MONTH),
    day: int = typer.Option(None, "--day", "-d", help=CliHelp.DAY),
    force: bool = typer.Option(False, "--force", help=CliHelp.FORCE),
) -> None:
    _caution_irreversible(force)
    params = {
        "process_type": process_type,
        "year": year,
        "month": month,
        "day": day
    }
    jsend_dict = safe_request("spectre-data/logs", 
                              "DELETE", 
                              params = params)
    file_names = jsend_dict["data"]
    _secho_deleted_files(file_names)
    raise typer.Exit()


@delete_app.command(
        help = ("Delete chunk files.")
)
def chunk_files(
    tag: str = typer.Option(..., "--tag", "-t", help=CliHelp.TAG),
    extension: list[str] = typer.Option(..., "--extension", "-e", help=CliHelp.EXTENSIONS),
    year: int = typer.Option(None, "--year", "-y", help=CliHelp.YEAR),
    month: int = typer.Option(None, "--month", "-m", help=CliHelp.MINUTES),
    day: int = typer.Option(None, "--day", "-d", help=CliHelp.DAY),
    force: bool = typer.Option(False, "--force", help=CliHelp.FORCE),
) -> None:
    _caution_irreversible(force)
    params = {
        "extension": extension,
        "year": year,
        "month": month,
        "day": day
    }
    jsend_dict = safe_request(f"spectre-data/chunks/{tag}", 
                              "DELETE",
                              params = params)
    file_names = jsend_dict["data"]
    _secho_deleted_files(file_names)
    raise typer.Exit()


@delete_app.command(
        help = ("Delete a capture config.")
)
def capture_config(
    tag: str = typer.Option(..., "--tag", "-t", help=CliHelp.TAG),
    force: bool = typer.Option(False, "--force", help="Bypass the irreversible action warning."),
) -> None:
    _caution_irreversible(force)
    jsend_dict = safe_request(f"spectre-data/capture-configs/{tag}", 
                              "DELETE")
    file_name = jsend_dict["data"]
    _secho_deleted_file(file_name)
    raise typer.Exit()
