# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typer import Typer, Option, Exit, secho
from typing import List

from ._utils import safe_request, get_capture_config_file_name


update_typer = Typer(
    help = "Update resources."
)

def _secho_updated_resource(
    endpoint: str
) -> None:    
    secho(endpoint, fg="green")


@update_typer.command(
        help = "Update capture config parameters."
)
def capture_config(tag: str = Option(None, 
                                     "--tag", 
                                     "-t", 
                                     help="Unique identifier for the capture config."),
                   file_name: str = Option(None, 
                                                "-f", 
                                                help="The file name of the capture config"),
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
   
    file_name = get_capture_config_file_name(file_name, tag)
    
    json = {
        "params": params,
        "force": force
    }
    jsend_dict = safe_request(f"spectre-data/configs/{file_name}",
                              "PATCH",
                              json = json)
    endpoint = jsend_dict["data"]
    _secho_updated_resource(endpoint)
    raise Exit()
