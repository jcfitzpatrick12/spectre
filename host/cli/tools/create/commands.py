# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from typing import List

from host.cli import __app_name__, __version__

from spectre.receivers.factory import get_receiver
from spectre.json_config.FitsConfigHandler import FitsConfigHandler


app = typer.Typer()

@app.command()
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
                params: List[str] = typer.Option([], "--param", "-p", help="Pass arbitrary key-value pairs.", metavar="KEY=VALUE")
) -> None:
    
    fits_config_handler = FitsConfigHandler(tag)
    fits_config_handler.save_params_as_fits_config(params)
    typer.secho(f"The fits-config for tag \"{tag}\" has been created.", fg=typer.colors.GREEN)
    raise typer.Exit()

@app.command()
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
                   receiver_name: str = typer.Option(..., "--receiver", "-r", help=""),
                   mode: str = typer.Option(..., "--mode", "-m", help=""),
                   params: List[str] = typer.Option([], "--param", "-p", help="Pass arbitrary key-value pairs.", metavar="KEY=VALUE"),
) -> None:
    
    receiver = get_receiver(receiver_name, mode = mode)
    receiver.save_params_as_capture_config(params, tag)
    typer.secho(f"The capture-config for tag \"{tag}\" has been created.", fg=typer.colors.GREEN)
    raise typer.Exit()

        

    

