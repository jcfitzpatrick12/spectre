# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from typing import List

from ._cli_help import CliHelp
from ._safe_request import safe_request

update_app = typer.Typer(
    help = "Update resources."
)

@update_app.command(
        help = "Update capture config parameters."
)
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=CliHelp.TAG),
                   params: List[str] = typer.Option(..., "--param", "-p", help="Pass arbitrary key-value pairs.", metavar="KEY=VALUE"),
                   force: bool = typer.Option(False, "--force", is_flag = True, help = CliHelp.FORCE_UPDATE)
) -> None:
    
    json = {
        "params": params,
        "force": force
    }
    jsend_dict = safe_request(f"spectre-data/configs/{tag}",
                              "PATCH",
                              json = json)
    file_name = jsend_dict["data"]

    typer.secho(f"Successfully updated `{file_name}`")

    raise typer.Exit()