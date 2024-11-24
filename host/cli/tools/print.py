# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer

from host.services import get
from host.cli import (
    PID_HELP,
    FILE_NAME_HELP,
    AS_COMMAND_HELP,
    TAG_HELP,
    RECEIVER_NAME_HELP,
    MODE_HELP
)

app = typer.Typer()
    
@app.command()
def log(
    pid: str = typer.Option(None, "--pid", help=PID_HELP),
    file_name: str = typer.Option(None, "--file-name", help=FILE_NAME_HELP)
) -> None:
    log_handler = get.log_handler(pid, file_name)
    log_handler.cat()
    raise typer.Exit()


@app.command()
def fits_config_type_template(
    tag: str = typer.Option(None, "--tag", "-t", help=TAG_HELP),
    as_command: bool = typer.Option(False, "--as-command", help=AS_COMMAND_HELP)
) -> None:
    type_template = get.fits_config_type_template(tag, as_command)
    if as_command:
        typer.secho(type_template)
    else:
        for k,v in type_template.items():
            typer.secho(f"{k}: {v.__name__}")
    typer.Exit()


@app.command()
def type_template(
    receiver_name: str = typer.Option(..., "--receiver", "-r", help=RECEIVER_NAME_HELP),
    mode: str = typer.Option(..., "--mode", "-m", help=MODE_HELP),
    as_command: bool = typer.Option(False, "--as-command", help=AS_COMMAND_HELP),
    tag: str = typer.Option(None, "--tag", "-t", help=TAG_HELP)
) -> None: 
    type_template = get.type_template(receiver_name, 
                                 mode, 
                                 as_command, 
                                 tag)
    if as_command:
        typer.secho(type_template)
    else:
        for k,v in type_template.items():
            typer.secho(f"{k}: {v.__name__}")
    typer.Exit()


@app.command()
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
) -> None:
    fits_config = get.fits_config(tag)
    for k, v in fits_config.items():
        typer.secho(f"{k}: {v}")
    raise typer.Exit()


@app.command()
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
) -> None:
    fits_config = get.capture_config(tag)
    for k, v in fits_config.items():
        typer.secho(f"{k}: {v}")
    raise typer.Exit()

    
