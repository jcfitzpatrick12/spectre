# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typer import Typer, secho, Option, Exit
import os

from spectre_core.config import get_spectre_data_dir_path

from ._safe_request import safe_request


delete_typer = Typer(
    help = "Delete resources."
)


def _secho_deleted_file(
    rel_path: str
) -> None:
    abs_path = os.path.join(get_spectre_data_dir_path(), rel_path)
    secho(f"Deleted '{abs_path}'", fg="yellow")
    
    
def _secho_deleted_files(
    rel_paths: list[str]
) -> None:    
    for rel_path in rel_paths:
        _secho_deleted_file(rel_path)


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
    rel_paths = jsend_dict["data"]
    _secho_deleted_files(rel_paths)
    raise Exit()


@delete_typer.command(
    help = "Delete batch files."
)
def batch_files(
    tag: str = Option(..., 
                      "--tag", 
                      "-t", 
                      help="The tag used to capture the data."),
    extension: list[str] = Option([], 
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
) -> None:
    params = {
        "extension": extension,
        "year": year,
        "month": month,
        "day": day
    }
    jsend_dict = safe_request(f"spectre-data/batches/{tag}", 
                              "DELETE",
                              params = params)
    rel_paths = jsend_dict["data"]
    _secho_deleted_files(rel_paths)
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
    rel_path = jsend_dict["data"]
    _secho_deleted_file(rel_path)
    raise Exit()
