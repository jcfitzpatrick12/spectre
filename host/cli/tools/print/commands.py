# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
import os

from host.cli import __app_name__, __version__

from spectre.file_handlers.json.FitsConfigHandler import FitsConfigHandler
from spectre.file_handlers.json.CaptureConfigHandler import CaptureConfigHandler
from spectre.receivers.factory import get_receiver

app = typer.Typer()

@app.command()
def fits_config_template(
    tag: str = typer.Option(None, "--tag", "-t", help=""),
    as_command: bool = typer.Option(False, "--as-command", help="")
) -> None:
    if as_command:
        if not tag:
            raise ValueError("If specifying --as-command, the tag must also be specified with --tag or -t.")
        fits_config_handler = FitsConfigHandler(tag)
        command_as_string = fits_config_handler.template_to_command(tag, as_string=True)
        typer.secho(command_as_string)
    else:
        template = FitsConfigHandler.get_template()
        for key, value in template.items():
            typer.secho(
                f"{key}: {value.__name__}"
            )
    typer.Exit()


@app.command()
def capture_config_template(
    receiver_name: str = typer.Option(..., "--receiver", "-r", help="Specify the receiver name"),
    mode: str = typer.Option(..., "--mode", "-m", help="Specify the mode for capture"),
    as_command: bool = typer.Option(False, "--as-command", help=""),
    tag: str = typer.Option(None, "--tag", "-t", help="")
) -> None:
    
    receiver = get_receiver(receiver_name, mode = mode)
    
    if as_command:
        if not tag:
            raise ValueError("If specifying --as-command, the tag must also be specified with --tag or -t.")
        command_as_string = receiver.template_to_command(tag, as_string=True)
        typer.secho(command_as_string)
    else:
        template = receiver.get_template()
        for key, value in template.items():
            typer.secho(
                f"{key}: {value.__name__}"
            )
    raise typer.Exit()


@app.command()
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
) -> None:
    fits_config_handler = FitsConfigHandler(tag)
    config_dict = fits_config_handler.read()
    for key, value in config_dict.items():
        typer.secho(
            f"{key}: {value}"
        )
    raise typer.Exit()

@app.command()
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
) -> None:
    capture_config_handler = CaptureConfigHandler(tag)
    config_dict = capture_config_handler.read()
    for key, value in config_dict.items():
        typer.secho(
            f"{key}: {value}"
        )
    raise typer.Exit()

    
