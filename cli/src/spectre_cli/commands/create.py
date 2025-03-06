# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from typer import Typer, Option, Exit, secho
from typing import List

from spectre_core.config import get_spectre_data_dir_path

from ._safe_request import safe_request

create_typer = Typer(
    help = "Create resources."
)

def _secho_created_file(
    rel_path: str
) -> None:    
    abs_path = os.path.join(get_spectre_data_dir_path(), rel_path)
    secho(f"Created '{abs_path}'", fg="green")


@create_typer.command(
    help = "Create a capture config."
)
def capture_config(
    tag: str = Option(..., 
                      "--tag", 
                      "-t", 
                      help="Unique identifier for the capture config."),
    receiver_name: str = Option(..., 
                               "--receiver",
                               "-r", 
                               help="The name of the receiver."),
    receiver_mode: str = Option(..., 
                                "--mode", 
                                "-m", 
                                help="The operating mode for the receiver."),
    params: List[str] = Option([], 
                               "--param", 
                               "-p", 
                               help="Parameters as key-value pairs.", 
                               metavar="KEY=VALUE"),
    force: bool = Option(False, 
                         "--force", 
                         help="If a capture config already exists with the same tag, "
                              "overwrite it.", 
                         is_flag=True)
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
    rel_path = jsend_dict["data"]
    _secho_created_file(rel_path)
    raise Exit()
        

    

