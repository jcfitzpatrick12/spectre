# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from typing import List
import requests

from spectre_cli import BASE_URL
from spectre_cli.commands import secho_response
from spectre_cli.commands import (
    RECEIVER_NAME_HELP,
    MODE_HELP,
    TAG_HELP,
    PARAMS_HELP,
    FORCE_HELP
)

app = typer.Typer()

@app.command()
@secho_response
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
                params: List[str] = typer.Option([], "--param", "-p", help=PARAMS_HELP, metavar="KEY=VALUE",),
                force: bool = typer.Option(False, "--force", help = FORCE_HELP, is_flag=True)
) -> None:
    
    payload = {
        "tag": tag,
        "params": params,
        "force": force
    }
    return requests.post(f"{BASE_URL}/create/fits-config",
                         json = payload)


@app.command()
@secho_response
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
                   receiver_name: str = typer.Option(..., "--receiver", "-r", help=RECEIVER_NAME_HELP),
                   mode: str = typer.Option(..., "--mode", "-m", help=MODE_HELP),
                   params: List[str] = typer.Option([], "--param", "-p", help=PARAMS_HELP, metavar="KEY=VALUE"),
                   force: bool = typer.Option(False, "--force", help = FORCE_HELP, is_flag=True)
) -> None:
    
    payload = {
        "tag": tag,
        "receiver_name": receiver_name,
        "mode": mode,
        "params": params,
        "force": force
    }
    return requests.post(f"{BASE_URL}/create/fits-config",
                         json = payload)

        

    

