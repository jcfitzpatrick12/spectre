# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from typing import List

from spectre_cli import (
    RECEIVER_NAME_HELP,
    MODE_HELP,
    TAG_HELP,
    PARAMS_HELP,
)

app = typer.Typer()

@app.command()
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
                params: List[str] = typer.Option([], "--param", "-p", help=PARAMS_HELP, metavar="KEY=VALUE")
) -> None:
    
    # create.capture_config(tag,
    #                       params)
    typer.secho(f"The fits-config for tag \"{tag}\" has been successfully created", fg=typer.colors.GREEN)
    raise typer.Exit()

@app.command()
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
                   receiver_name: str = typer.Option(..., "--receiver", "-r", help=RECEIVER_NAME_HELP),
                   mode: str = typer.Option(..., "--mode", "-m", help=MODE_HELP),
                   params: List[str] = typer.Option([], "--param", "-p", help=PARAMS_HELP, metavar="KEY=VALUE"),
) -> None:
    
    # create.capture_config(tag,
    #                       receiver_name,
    #                       mode,
    #                       params)
    typer.secho(f"The capture-config for tag \"{tag}\" has been successfully created", fg=typer.colors.GREEN)
    raise typer.Exit()

        

    

