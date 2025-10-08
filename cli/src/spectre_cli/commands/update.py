# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typer import Typer, Option, Exit, secho
from typing import List

from ._utils import safe_request, get_config_file_name


update_typer = Typer(help="Update resources.")


def _secho_updated_resource(endpoint: str) -> None:
    secho(endpoint, fg="green")


@update_typer.command(help="Update capture config parameters.", deprecated=True)
def capture_config(
    tag: str = Option(None, "--tag", "-t", help="The unique identifier."),
    file_name: str = Option(None, "-f", help="The file name.", metavar="<tag>.json"),
    params: List[str] = Option(
        [],
        "--param",
        "-p",
        help="Parameters as key-value pairs.",
        metavar="<key>=<value>",
    ),
    force: bool = Option(
        False,
        "--force",
        help="If specified, force the operation even if files exist with the same tag.",
    ),
    skip_validation: bool = Option(
        False,
        "--skip-validation",
        help="If specified, do not validate the parameters.",
    ),
) -> None:

    file_name = get_config_file_name(file_name, tag)

    json = {"params": params, "force": force, "validate": not skip_validation}
    jsend_dict = safe_request(f"spectre-data/configs/{file_name}", "PATCH", json=json)
    endpoint = jsend_dict["data"]
    _secho_updated_resource(endpoint)
    raise Exit()


@update_typer.command(help="Update config parameters.")
def config(
    tag: str = Option(None, "--tag", "-t", help="The unique identifier."),
    file_name: str = Option(None, "-f", help="The file name.", metavar="<tag>.json"),
    params: List[str] = Option(
        [],
        "--param",
        "-p",
        help="Parameters as key-value pairs.",
        metavar="<key>=<value>",
    ),
    force: bool = Option(
        False,
        "--force",
        help="If specified, force the operation even if files exist with the same tag.",
    ),
    skip_validation: bool = Option(
        False,
        "--skip-validation",
        help="If specified, do not validate the parameters.",
    ),
) -> None:

    file_name = get_config_file_name(file_name, tag)

    json = {"params": params, "force": force, "validate": not skip_validation}
    jsend_dict = safe_request(f"spectre-data/configs/{file_name}", "PATCH", json=json)
    endpoint = jsend_dict["data"]
    _secho_updated_resource(endpoint)
    raise Exit()
