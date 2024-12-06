# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from typing import List

from spectre_cli.commands import safe_request
from spectre_cli.commands import (
    RECEIVER_NAME_HELP,
    MODE_HELP,
    TAG_HELP,
    PARAMS_HELP,
    FORCE_HELP
)

create_app = typer.Typer()

@create_app.command()
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
                params: List[str] = typer.Option([], "--param", "-p", help=PARAMS_HELP, metavar="KEY=VALUE",),
                force: bool = typer.Option(False, "--force", help = FORCE_HELP, is_flag=True)
) -> None:
    
    json = {
        "params": params,
        "force": force
    }
    jsend_dict = safe_request(f"spectre-data/configs/fits/{tag}", 
                              "PUT", 
                              json = json)
    file_name = jsend_dict["data"]
    typer.secho(f"Fits config created successfully with tag '{tag}': {file_name}")
    raise typer.Exit()


@create_app.command()
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
                   receiver_name: str = typer.Option(..., "--receiver", "-r", help=RECEIVER_NAME_HELP),
                   mode: str = typer.Option(..., "--mode", "-m", help=MODE_HELP),
                   params: List[str] = typer.Option([], "--param", "-p", help=PARAMS_HELP, metavar="KEY=VALUE"),
                   force: bool = typer.Option(False, "--force", help = FORCE_HELP, is_flag=True)
) -> None:
    
    json = {
        "receiver_name": receiver_name,
        "mode": mode,
        "params": params,
        "force": force
    }
    jsend_dict = safe_request("spectre-data/configs/fits/{tag}", 
                              "PUT", 
                              json = json)
    file_name = jsend_dict["data"]
    typer.secho(f"Capture config created successfully with tag '{tag}': {file_name}")
    raise typer.Exit()
        

    

