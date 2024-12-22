# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from typing import List

from spectre_cli.commands import safe_request
from spectre_cli.commands import CliHelp

create_app = typer.Typer(
    help = "Create resources."
)

@create_app.command(
        help = ("Create a capture config.")
)
def capture_config(
    tag: str = typer.Option(..., "--tag", "-t", help=CliHelp.TAG),
    receiver_name: str = typer.Option(..., "--receiver", "-r", help=CliHelp.RECEIVER_NAME),
    mode: str = typer.Option(..., "--mode", "-m", help=CliHelp.MODE),
    params: List[str] = typer.Option([], "--param", "-p", help=CliHelp.PARAM, metavar="KEY=VALUE"),
    force: bool = typer.Option(False, "--force", help = CliHelp.FORCE, is_flag=True)
) -> None:
    
    json = {
        "receiver_name": receiver_name,
        "mode": mode,
        "params": params,
        "force": force
    }
    jsend_dict = safe_request(f"spectre-data/capture-configs/{tag}", 
                              "PUT", 
                              json = json)
    file_name = jsend_dict["data"]
    typer.secho(f"Capture config created successfully with tag '{tag}': {file_name}")
    raise typer.Exit()
        

    

