# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typer import Typer, Option, Exit, secho
from typing import List

from ._safe_request import safe_request


update_typer = Typer(
    help = "Update resources."
)

def _secho_updated_file(
    abs_path: str
) -> None:    
    secho(f"Updated '{abs_path}'", fg="green")


@update_typer.command(
        help = "Update capture config parameters."
)
def capture_config(tag: str = Option(..., 
                                     "--tag", 
                                     "-t", 
                                     help="Unique identifier for the capture config."),
                   params: List[str] = Option(..., 
                                              "--param", 
                                              "-p", 
                                              help="Pass arbitrary key-value pairs.", 
                                              metavar="KEY=VALUE"),
                   force: bool = Option(False, 
                                        "--force", 
                                        is_flag=True, 
                                        help="Force the update even if data has already been collected under this capture config. "
                                             "Use with caution: existing data may no longer align with the updated configuration, "
                                             "potentially leading to misleading results.")
) -> None:
    
    json = {
        "params": params,
        "force": force
    }
    jsend_dict = safe_request(f"spectre-data/configs/{tag}",
                              "PATCH",
                              json = json)
    abs_path = jsend_dict["data"]
    _secho_updated_file(abs_path)
    raise Exit()