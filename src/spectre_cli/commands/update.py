# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from typing import List

from spectre_cli.commands import safe_request
from spectre_cli.commands import CliHelp

update_app = typer.Typer(
    help = "Update resources."
)

@update_app.command(
        help = ("Update a capture config.")
)
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=CliHelp.TAG),
                   params: List[str] = typer.Option(..., "--param", "-p", help="Pass arbitrary key-value pairs.", metavar="KEY=VALUE"),
                   force: bool = typer.Option(False, "--force", is_flag = True, help = CliHelp.FORCE_UPDATE)
) -> None:
    
    json = {
        "params": params,
        "force": force
    }
    jsend_dict = safe_request(f"spectre-data/capture-configs/{tag}",
                              "PATCH",
                              json = json)
    file_name = jsend_dict["data"]

    typer.secho(f"Successfully updated `{file_name}`")

    raise typer.Exit()