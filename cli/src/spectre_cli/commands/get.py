# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typer import Typer, Option, Exit, secho

from ._utils import safe_request, get_capture_config_file_name
from ._secho_resources import pprint_dict, secho_existing_resources


get_typer = Typer(help="Display one or many resources.")


@get_typer.command(help="List e-Callisto network instrument codes.")
def callisto_instrument_codes() -> None:
    jsend_dict = safe_request("callisto/instrument-codes", "GET")
    callisto_instrument_codes = jsend_dict["data"]

    for instrument_code in callisto_instrument_codes:
        secho(instrument_code)

    raise Exit()


@get_typer.command(help="List log files.")
def logs(
    process_types: list[str] = Option(
        [],
        "--process-type",
        help="List all logs with this process type. Specifies one of 'worker' or 'user'. If not provided, list log files with any process type.",
    ),
    year: int = Option(
        None, "--year", "-y", help="Only list log files under this year."
    ),
    month: int = Option(
        None, "--month", "-m", help="Only list log files under this month."
    ),
    day: int = Option(None, "--day", "-d", help="Only list log files under this day."),
) -> None:
    params = {"process_type": process_types, "year": year, "month": month, "day": day}
    jsend_dict = safe_request(f"spectre-data/logs", "GET", params=params)
    endpoints = jsend_dict["data"]

    secho_existing_resources(endpoints)
    raise Exit()


@get_typer.command(help="Print the contents of a log file.")
def log(
    file_name: str = Option(..., "-f", help="The file name."),
) -> None:
    jsend_dict = safe_request(f"spectre-data/logs/{file_name}/raw", "GET")
    log_contents = jsend_dict["data"]
    print(log_contents)
    raise Exit()


@get_typer.command(help="List batch files.")
def batch_files(
    extensions: list[str] = Option(
        [],
        "--extension",
        "-e",
        help="List all batch files with this file extension. If not provided, list batch files with any extension.",
    ),
    tags: list[str] = Option(
        [],
        "--tag",
        "-t",
        help="List all batch files with this tag. If not provided, list batch files with any tag.",
    ),
    year: int = Option(
        None, "--year", "-y", help="Only list batch files under this numeric year."
    ),
    month: int = Option(
        None, "--month", "-m", help="Only list batch files under this month."
    ),
    day: int = Option(
        None, "--day", "-d", help="Only list batch files under this day."
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
    raise Exit()


@get_typer.command(help="List supported receivers.")
def receivers() -> None:

    jsend_dict = safe_request("receivers", "GET")
    receiver_names = jsend_dict["data"]

    for receiver_name in receiver_names:
        secho(receiver_name)

    raise Exit()


@get_typer.command(help=("List the supported operating modes for a receiver."))
def modes(
    receiver_name: str = Option(
        ..., "--receiver", "-r", help="The name of the receiver."
    )
) -> None:

    jsend_dict = safe_request(f"receivers/{receiver_name}/modes", "GET")
    receiver_modes = jsend_dict["data"]

    for receiver_mode in receiver_modes:
        secho(receiver_mode)

    raise Exit()


@get_typer.command(help="Print receiver hardware specifications.")
def specs(
    receiver_name: str = Option(
        ..., "--receiver", "-r", help="The name of the receiver."
    )
) -> None:

    params = {"receiver_name": receiver_name}
    jsend_dict = safe_request(f"receivers/{receiver_name}/specs", "GET", params=params)
    specs = jsend_dict["data"]

    for k, v in specs.items():
        secho(f"{k}: {v}")

    raise Exit()


@get_typer.command(help="List capture configs.")
def capture_configs() -> None:

    jsend_dict = safe_request(f"spectre-data/configs", "GET")
    endpoints = jsend_dict["data"]
    secho_existing_resources(endpoints)
    raise Exit()


@get_typer.command(help="Print capture config file contents.")
def capture_config(
    tag: str = Option(None, "--tag", "-t", help="The unique identifier."),
    file_name: str = Option(None, "-f", help="The file name.", metavar="<tag>.json"),
) -> None:

    file_name = get_capture_config_file_name(file_name, tag)

    jsend_dict = safe_request(f"spectre-data/configs/{file_name}/raw", "GET")
    capture_config = jsend_dict["data"]
    pprint_dict(capture_config)
    raise Exit()


@get_typer.command(help="List tags with existing batch files.")
def tags(
    year: int = Option(
        None,
        "--year",
        "-y",
        help="Only list tags under this year.",
    ),
    month: int = Option(
        None,
        "--month",
        "-m",
        help="Only list tags under this month.",
    ),
    day: int = Option(
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
        secho(tag)

    raise Exit()


@get_typer.command(help="Print a capture template.")
def capture_template(
    receiver_name: str = Option(
        ..., "--receiver", "-r", help="The name of the receiver."
    ),
    receiver_mode: str = Option(
        ..., "--mode", "-m", help="The operating mode of the receiver."
    ),
    param_name: str = Option(
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

    Exit()
