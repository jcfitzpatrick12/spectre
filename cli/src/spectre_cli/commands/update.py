# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typer import Typer, Option, Exit, secho
from typing import List

from ._safe_request import safe_request


update_typer = Typer(
    help = "Update resources."
)

def _secho_updated_resource(
    resource_endpoint: str
) -> None:    
    secho(resource_endpoint, fg="green")


@update_typer.command(
        help = "Update capture config parameters."
)
def capture_config(tag: str = Option(None, 
                                     "--tag", 
                                     "-t", 
                                     help="Unique identifier for the capture config."),
                   base_file_name: str = Option(None, 
                                                "-f", 
                                                help="The base file name of the capture config"),
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
   
    if not (base_file_name is None) ^ (tag is None):
        raise ValueError("Specify either the tag or file name, not both.")
                                                                           
    base_file_name = base_file_name or f"{tag}.json"
    
    json = {
        "params": params,
        "force": force
    }
    jsend_dict = safe_request(f"spectre-data/configs/{base_file_name}",
                              "PATCH",
                              json = json)
    resource_endpoint = jsend_dict["data"]
    _secho_updated_resource(resource_endpoint)
    raise Exit()
