# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from typing import List

from ._utils import safe_request, get_config_file_name
from ._secho_resources import secho_new_resource


update_typer = typer.Typer(help="Update resources.")


@update_typer.command(help="Update config parameters.")
def config(
    tag: str = typer.Option(None, "--tag", "-t", help="The unique identifier."),
    file_name: str = typer.Option(
        None, "-f", help="The file name.", metavar="<tag>.json"
    ),
    params: List[str] = typer.Option(
        [],
        "--param",
        "-p",
        help="Parameters as key-value pairs.",
        metavar="<key>=<value>",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="If specified, force the operation even if files exist with the same tag.",
    ),
    skip_validation: bool = typer.Option(
        False,
        "--skip-validation",
        help="If specified, do not validate the parameters.",
    ),
) -> None:

    file_name = get_config_file_name(file_name, tag)

    json = {"params": params, "force": force, "validate": not skip_validation}
    jsend_dict = safe_request(f"spectre-data/configs/{file_name}", "PATCH", json=json)
    endpoint = jsend_dict["data"]
    secho_new_resource(endpoint)
    raise typer.Exit()
