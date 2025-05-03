# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typer import Typer, Option, Exit

from ._utils import safe_request, build_date_path, get_capture_config_file_name
from ._secho_resources import secho_stale_resource, secho_stale_resources


delete_typer = Typer(
    help = "Delete resources."
)
        

@delete_typer.command(
    help = "Delete log files."
)
def logs(
    process_types: list[str] = Option([], 
                                     "--process-type",                                
                                     help="Specifies one of 'worker' or 'user'."),
    year: int = Option(None, 
                       "--year", 
                       "-y", 
                       help="Delete logs under this numeric year."),
    month: int = Option(None, 
                       "--month", 
                       "-m", 
                       help="Delete logs under this numeric month."),
    day: int = Option(None, 
                      "--day", 
                      "-d", 
                      help="Delete  logs under this numeric day."),
    suppress_confirmation: bool = Option(False, 
                                         "--suppress-confirmation", 
                                         help="Suppress any user confirmation.")
    
) -> None:
    params = {
        "process_type": process_types,
    }
    jsend_dict = safe_request(f"spectre-data/logs/{build_date_path(year, month, day)}", 
                              "DELETE", 
                              params=params,
                              require_confirmation=True,
                              suppress_confirmation=suppress_confirmation)
    endpoints = jsend_dict["data"]
    secho_stale_resources(endpoints)
    raise Exit()


@delete_typer.command(
    help = "Delete batch files."
)
def batch_files(
    tags: list[str] = Option([], 
                             "--tag", 
                             "-t", 
                             help="The tag used to capture the data."),
    extensions: list[str] = Option([], 
                                  "--extension", 
                                  "-e", 
                                  help="Delete all batch files with this file extension."),
    year: int = Option(None, 
                      "--year", 
                      "-y", 
                      help="Delete all batch files under this numeric year."),
    month: int = Option(None, 
                        "--month", 
                        "-m", 
                        help="Delete all batch files under this numeric month."),
    day: int = Option(None, 
                      "--day", 
                      "-d", 
                      help="Delete all batch files under this numeric day."),
    suppress_confirmation: bool = Option(False, 
                                         "--suppress-confirmation", 
                                         help="Suppress any user confirmation.")
) -> None:
    params = {
        "extension": extensions,
        "tag": tags
    }
    jsend_dict = safe_request(f"spectre-data/batches/{build_date_path(year, month, day)}", 
                              "DELETE",
                              params = params,
                              require_confirmation=True,
                              suppress_confirmation=suppress_confirmation)
    endpoints = jsend_dict["data"]
    secho_stale_resources(endpoints)
    raise Exit()


@delete_typer.command(
    help = "Delete a capture config."
)
def capture_config(
    tag: str = Option(None, 
                      "--tag", 
                      "-t", 
                      help="Unique identifier for the capture config."),
    file_name: str = Option(None,
                            "-f",
                            help="The file name of the capture config."),
    suppress_confirmation: bool = Option(False, 
                         "--suppress-confirmation", 
                         help="Suppress any user confirmation.")
) -> None:
    
                                                                           
    file_name = get_capture_config_file_name(file_name, tag)

    jsend_dict = safe_request(f"spectre-data/configs/{tag}.json", 
                              "DELETE",
                              require_confirmation=True,
                              suppress_confirmation=suppress_confirmation)
    endpoint = jsend_dict["data"]
    secho_stale_resource(endpoint)
    raise Exit()
