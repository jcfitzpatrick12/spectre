# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from typing import List

from ._cli_help import CliHelp
from ._safe_request import safe_request

create_typer = typer.Typer(
    help = "Create resources."
)

@create_typer.command(
        help = "Create a capture config."
)
def capture_config(
    tag: str = typer.Option(..., "--tag", "-t", help=CliHelp.TAG),
    receiver_name: str = typer.Option(..., "--receiver", "-r", help=CliHelp.RECEIVER_NAME),
    receiver_mode: str = typer.Option(..., "--mode", "-m", help=CliHelp.MODE),
    params: List[str] = typer.Option([], "--param", "-p", help=CliHelp.PARAM, metavar="KEY=VALUE"),
    force: bool = typer.Option(False, "--force", help = CliHelp.FORCE, is_flag=True)
) -> None:
    json = {
        "receiver_name": receiver_name,
        "receiver_mode": receiver_mode,
        "string_parameters": params,
        "force": force
    }
    jsend_dict = safe_request(f"spectre-data/configs/{tag}", 
                              "PUT", 
                              json=json)
    file_name = jsend_dict["data"]
    typer.secho(f"Created '{file_name}'")
    raise typer.Exit()
        

    

