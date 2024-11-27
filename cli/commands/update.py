# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from typing import List

from cli import (
    TAG_HELP,
    FORCE_UPDATE_HELP
)

app = typer.Typer()

@app.command()
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
                   params: List[str] = typer.Option(..., "--param", "-p", help="Pass arbitrary key-value pairs.", metavar="KEY=VALUE"),
                   force: bool = typer.Option(False, "--force", is_flag = True, help = FORCE_UPDATE_HELP)
) -> None:
    # update.capture_config(tag, 
    #                       params, 
    #                       force = force)
    # typer.secho(f"The capture-config for tag \"{tag}\" has been successfully updated", fg=typer.colors.GREEN)
    raise typer.Exit()


@app.command()
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
                params: List[str] = typer.Option(..., "--param", "-p", help="Pass arbitrary key-value pairs.", metavar="KEY=VALUE"),
                force: bool = typer.Option(False, "--force", is_flag = True, help = FORCE_UPDATE_HELP)
) -> None:
    # update.fits_config(tag, 
    #                    params,
    #                    force)
    # typer.secho(f"The fits-config for tag \"{tag}\" has been successfully updated", fg=typer.colors.GREEN)
    raise typer.Exit()