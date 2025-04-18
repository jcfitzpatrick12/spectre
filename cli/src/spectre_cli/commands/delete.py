# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typer import Typer, secho, Option, Exit

from ._safe_request import safe_request


delete_typer = Typer(
    help = "Delete resources."
)


def _secho_deleted_resource(
    resource_endpoint: str
) -> None:
    secho(resource_endpoint, fg="yellow")
    
    
def _secho_deleted_resources(
    resource_endpoints: list[str]
) -> None:    
    for resource_endpoint in resource_endpoints:
        _secho_deleted_resource(resource_endpoint)


@delete_typer.command(
    help = "Delete log files."
)
def logs(
    year: int = Option(..., 
                       "--year", 
                       "-y", 
                       help="Delete logs under this numeric year."),
    month: int = Option(..., 
                       "--month", 
                       "-m", 
                       help="Delete logs under this numeric month."),
    day: int = Option(..., 
                      "--day", 
                      "-d", 
                      help="Delete  logs under this numeric day."),
    process_types: list[str] = Option([], 
                                     "--process-type",                                
                                     help="Specifies one of 'worker' or 'user'."),

) -> None:
    params = {
        "process_type": process_types,
    }
    jsend_dict = safe_request(f"spectre-data/logs/{year}/{month}/{day}", 
                              "DELETE", 
                              params = params)
    resource_endpoints = jsend_dict["data"]
    _secho_deleted_resources(resource_endpoints)
    raise Exit()


@delete_typer.command(
    help = "Delete batch files."
)
def batch_files(
    year: int = Option(..., 
                      "--year", 
                      "-y", 
                      help="Delete all batch files under this numeric year."),
    month: int = Option(..., 
                        "--month", 
                        "-m", 
                        help="Delete all batch files under this numeric month."),
    day: int = Option(..., 
                      "--day", 
                      "-d", 
                      help="Delete all batch files under this numeric day."),
    tags: list[str] = Option([], 
                             "--tag", 
                             "-t", 
                             help="The tag used to capture the data."),
    extensions: list[str] = Option([], 
                                  "--extension", 
                                  "-e", 
                                  help="Delete all batch files with this file extension."),
) -> None:
    params = {
        "extension": extensions,
        "tag": tags
    }
    jsend_dict = safe_request(f"spectre-data/batches/{year}/{month}/{day}", 
                              "DELETE",
                              params = params)
    resource_endpoints = jsend_dict["data"]
    _secho_deleted_resources(resource_endpoints)
    raise Exit()


@delete_typer.command(
    help = "Delete a capture config."
)
def capture_config(
    tag: str = Option(..., 
                      "--tag", 
                      "-t", 
                      help="Unique identifier for the capture config."),
) -> None:
    jsend_dict = safe_request(f"spectre-data/configs/{tag}.json", 
                              "DELETE")
    resource_endpoint = jsend_dict["data"]
    _secho_deleted_resource(resource_endpoint)
    raise Exit()
