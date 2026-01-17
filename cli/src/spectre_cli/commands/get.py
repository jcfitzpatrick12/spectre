# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer

from ..config import SPECTRE_SERVER
from ._utils import safe_request, get_config_file_name, download_file, download_files
from ._secho_resources import (
    pprint_dict,
    secho_existing_resource,
    secho_existing_resources,
)


get_typer = typer.Typer(help="Display one or many resources.")


@get_typer.command(help="List logs.")
def logs(
    process_types: list[str] = typer.Option(
        [],
        "--process-type",
        help="List all logs with this process type, specifying one of 'worker' or 'user'. If not provided, list logs with any process type.",
    ),
    year: int = typer.Option(
        None, "--year", "-y", help="Only list logs under this year."
    ),
    month: int = typer.Option(
        None, "--month", "-m", help="Only list logs under this month."
    ),
    day: int = typer.Option(None, "--day", "-d", help="Only list logs under this day."),
    output_dir: str = typer.Option(
        None, "-o", help="Directory to save the downloaded files."
    ),
) -> None:
    params = {"process_type": process_types, "year": year, "month": month, "day": day}
    jsend_dict = safe_request(f"spectre-data/logs", "GET", params=params)
    endpoints = jsend_dict["data"]

    if output_dir:
        # Download mode: download all log files
        download_files(endpoints, output_dir)
    else:
        # Display mode: list the endpoints
        secho_existing_resources(endpoints)

    raise typer.Exit()


@get_typer.command(help="Print the contents of a log.")
def log(
    file_name: str = typer.Option(..., "-f", help="The file name."),
    output_dir: str = typer.Option(
        None, "-o", help="Directory to save the downloaded file."
    ),
) -> None:
    if output_dir:
        # Download mode: use the direct endpoint to download the file
        # The backend's get_log endpoint returns the file directly
        log_url = f"{SPECTRE_SERVER}/spectre-data/logs/{file_name}"
        download_file(log_url, output_dir)
    else:
        # Display mode: print the log contents
        jsend_dict = safe_request(f"spectre-data/logs/{file_name}/raw", "GET")
        log_contents = jsend_dict["data"]
        print(log_contents)

    raise typer.Exit()


@get_typer.command(help="List files.")
def files(
    extensions: list[str] = typer.Option(
        [],
        "--extension",
        "-e",
        help="List all files with this file extension. If not provided, list files with any extension.",
    ),
    tags: list[str] = typer.Option(
        [],
        "--tag",
        "-t",
        help="List all files with this tag. If not provided, list files with any tag.",
    ),
    year: int = typer.Option(
        None, "--year", "-y", help="Only list files under this year."
    ),
    month: int = typer.Option(
        None, "--month", "-m", help="Only list files under this month."
    ),
    day: int = typer.Option(
        None, "--day", "-d", help="Only list files under this day."
    ),
    output_dir: str = typer.Option(
        None, "-o", help="Directory to save the downloaded files."
    ),
) -> None:
    params = {
        "extension": extensions,
        "tag": tags,
        "year": year,
        "month": month,
        "day": day,
    }
    jsend_dict = safe_request(
        f"spectre-data/batches",
        "GET",
        params=params,
    )
    endpoints = jsend_dict["data"]

    if output_dir:
        # Download mode: download all batch files
        download_files(endpoints, output_dir)
    else:
        # Display mode: list the endpoints
        secho_existing_resources(endpoints)

    raise typer.Exit()


@get_typer.command(help="List supported receivers.")
def receivers() -> None:

    jsend_dict = safe_request("receivers", "GET")
    receiver_names = jsend_dict["data"]

    for receiver_name in receiver_names:
        secho_existing_resource(receiver_name)

    raise typer.Exit()


@get_typer.command(help=("List the supported operating modes for a receiver."))
def modes(
    receiver_name: str = typer.Option(
        ..., "--receiver", "-r", help="The name of the receiver."
    )
) -> None:

    jsend_dict = safe_request(f"receivers/{receiver_name}/modes", "GET")
    receiver_modes = jsend_dict["data"]

    for receiver_mode in receiver_modes:
        secho_existing_resource(receiver_mode)

    raise typer.Exit()


@get_typer.command(help="List configs.")
def configs(
    output_dir: str = typer.Option(
        None, "-o", help="Directory to save the downloaded files."
    ),
) -> None:

    jsend_dict = safe_request(f"spectre-data/configs", "GET")
    endpoints = jsend_dict["data"]

    if output_dir:
        # Download mode: download all config files
        download_files(endpoints, output_dir)
    else:
        # Display mode: list the endpoints
        secho_existing_resources(endpoints)

    raise typer.Exit()


@get_typer.command(help="Print config file contents.")
def config(
    tag: str = typer.Option(None, "--tag", "-t", help="The unique identifier."),
    file_name: str = typer.Option(
        None, "-f", help="The file name.", metavar="<tag>.json"
    ),
    output_dir: str = typer.Option(
        None, "-o", help="Directory to save the downloaded file."
    ),
) -> None:

    file_name = get_config_file_name(file_name, tag)

    if output_dir:
        # Download mode: use the direct endpoint to download the file
        # The backend's get_config endpoint returns the file directly
        config_url = f"{SPECTRE_SERVER}/spectre-data/configs/{file_name}"
        download_file(config_url, output_dir)
    else:
        # Display mode: print the config contents
        jsend_dict = safe_request(f"spectre-data/configs/{file_name}/raw", "GET")
        config = jsend_dict["data"]
        pprint_dict(config)

    raise typer.Exit()


@get_typer.command(help="List tags with existing files.")
def tags(
    year: int = typer.Option(
        None,
        "--year",
        "-y",
        help="Only list tags under this year.",
    ),
    month: int = typer.Option(
        None,
        "--month",
        "-m",
        help="Only list tags under this month.",
    ),
    day: int = typer.Option(
        None,
        "--day",
        "-d",
        help="Only list tags under this day.",
    ),
) -> None:
    params = {"year": year, "month": month, "day": day}
    url = (
        f"spectre-data/batches/tags"
        if year is not None
        else "spectre-data/batches/tags"
    )
    jsend_dict = safe_request(url, "GET", params=params)
    tags = jsend_dict["data"]

    for tag in tags:
        secho_existing_resource(tag)

    raise typer.Exit()


@get_typer.command(help="Print a model.")
def model(
    receiver_name: str = typer.Option(
        ..., "--receiver", "-r", help="The name of the receiver."
    ),
    receiver_mode: str = typer.Option(
        ..., "--mode", "-m", help="The operating mode of the receiver."
    ),
) -> None:

    params = {
        "receiver_mode": receiver_mode,
    }
    jsend_dict = safe_request(f"receivers/{receiver_name}/model", "GET", params=params)
    model = jsend_dict["data"]
    pprint_dict(model)
    typer.Exit()
