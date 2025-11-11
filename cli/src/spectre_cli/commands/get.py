# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer

from ._utils import safe_request, get_config_file_name
from ._secho_resources import (
    pprint_dict,
    secho_existing_resource,
    secho_existing_resources,
)


get_typer = typer.Typer(help="Display one or many resources.")


@get_typer.command(help="List e-Callisto network instrument codes.")
def callisto_instrument_codes() -> None:
    jsend_dict = safe_request("callisto/instrument-codes", "GET")
    callisto_instrument_codes = jsend_dict["data"]

    for instrument_code in callisto_instrument_codes:
        secho_existing_resource(instrument_code)

    raise typer.Exit()


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
) -> None:
    params = {"process_type": process_types, "year": year, "month": month, "day": day}
    jsend_dict = safe_request(f"spectre-data/logs", "GET", params=params)
    endpoints = jsend_dict["data"]

    secho_existing_resources(endpoints)
    raise typer.Exit()


@get_typer.command(help="Print the contents of a log.")
def log(
    file_name: str = typer.Option(..., "-f", help="The file name."),
) -> None:
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


@get_typer.command(help="Print receiver hardware specifications.")
def specs(
    receiver_name: str = typer.Option(
        ..., "--receiver", "-r", help="The name of the receiver."
    )
) -> None:

    params = {"receiver_name": receiver_name}
    jsend_dict = safe_request(f"receivers/{receiver_name}/specs", "GET", params=params)
    specs = jsend_dict["data"]

    for k, v in specs.items():
        secho_existing_resource(f"{k}: {v}")

    raise typer.Exit()


@get_typer.command(help="List configs.")
def configs() -> None:

    jsend_dict = safe_request(f"spectre-data/configs", "GET")
    endpoints = jsend_dict["data"]
    secho_existing_resources(endpoints)
    raise typer.Exit()


@get_typer.command(help="Print config file contents.")
def config(
    tag: str = typer.Option(None, "--tag", "-t", help="The unique identifier."),
    file_name: str = typer.Option(
        None, "-f", help="The file name.", metavar="<tag>.json"
    ),
) -> None:

    file_name = get_config_file_name(file_name, tag)

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


@get_typer.command(help="Print a capture template.")
def capture_template(
    receiver_name: str = typer.Option(
        ..., "--receiver", "-r", help="The name of the receiver."
    ),
    receiver_mode: str = typer.Option(
        ..., "--mode", "-m", help="The operating mode of the receiver."
    ),
    param_name: str = typer.Option(
        None,
        "--param",
        "-p",
        help="The name of the parameter to print a template for. If not provided, prints the full capture template.",
    ),
) -> None:

    params = {
        "receiver_mode": receiver_mode,
    }
    jsend_dict = safe_request(
        f"receivers/{receiver_name}/capture-template", "GET", params=params
    )
    capture_template = jsend_dict["data"]

    if param_name is None:
        pprint_dict(capture_template)
    else:
        if param_name not in capture_template:
            raise KeyError(
                f"A parameter with name '{param_name}' does not exist "
                f"in the capture template for the receiver '{receiver_name}' "
                f"operating in mode '{receiver_mode}'. Expected one of: "
                f"{list(capture_template.keys())}"
            )
        pprint_dict(capture_template[param_name])

    typer.Exit()
