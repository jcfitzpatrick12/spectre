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
    process_type: str = Option(None, 
                               "--process-type", 
                               help="Specifies one of 'worker' or 'user'."),
    year: int = Option(None, 
                       "--year", 
                       "-y", 
                       help="Delete all logs under this numeric year."),
    month: int = Option(None, 
                       "--month", 
                       "-m", 
                      help="Delete all logs under this numeric month."),
    day: int = Option(None, 
                      "--day", 
                      "-d", 
                      help="Delete all logs under this numeric day.")
) -> None:
    params = {
        "process_type": process_type,
        "year": year,
        "month": month,
        "day": day,
    }
    jsend_dict = safe_request("spectre-data/logs", 
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
    jsend_dict = safe_request(f"spectre-data/configs/{tag}", 
                              "DELETE")
    resource_endpoint = jsend_dict["data"]
    _secho_deleted_resource(resource_endpoint)
    raise Exit()
