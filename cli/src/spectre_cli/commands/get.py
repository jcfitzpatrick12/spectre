# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import os
import re
import typer
import requests

import astropy.io.fits

from ._utils import safe_request, get_config_file_name
from ._secho_resources import (
    pprint_dict,
    secho_existing_resource,
    secho_existing_resources,
)


def __download_resource(endpoint: str, directory: str) -> None:
    file_path = os.path.join(directory, os.path.basename(endpoint))
    response = requests.get(endpoint)
    with open(file_path, "wb") as file:
        file.write(response.content)


def __download_resources(endpoints: list[str], directory: str) -> None:
    os.makedirs(directory, exist_ok=True)
    for endpoint in endpoints:
        __download_resource(endpoint, directory)


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
    export: str = typer.Option(
        None,
        "--export",
        help="Bulk download logs to your local filesystem inside this directory.",
    ),
) -> None:
    params = {"process_type": process_types, "year": year, "month": month, "day": day}
    jsend_dict = safe_request(f"spectre-data/logs", "GET", params=params)
    endpoints = jsend_dict["data"]

    if export is None:
        secho_existing_resources(endpoints)
    else:
        __download_resources(endpoints, export)
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
    export: str = typer.Option(
        None,
        "--export",
        help="Bulk download files to your local filesystem inside this directory.",
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

    if export is None:
        secho_existing_resources(endpoints)
    else:
        __download_resources(endpoints, export)

    raise typer.Exit()


_FOCUS_CODE_RE = re.compile(r"^\d{2}$")


def __rename_to_ecallisto(file_path: str, focus_code: str) -> str:
    """Rewrite ``file_path`` to ``{INSTRUME}_{YYYYMMDD}_{HHMMSS}_{focus_code}.fit`` in place."""
    with astropy.io.fits.open(file_path) as hdul:
        header = hdul[0].header
        instrume = header.get("INSTRUME")
        date_obs = header.get("DATE-OBS")
        time_obs = header.get("TIME-OBS")

    if not (instrume and date_obs and time_obs):
        raise ValueError(
            f"missing one of INSTRUME / DATE-OBS / TIME-OBS in {os.path.basename(file_path)}"
        )

    dt = datetime.datetime.strptime(
        f"{date_obs} {time_obs}", "%Y/%m/%d %H:%M:%S.%f"
    )
    canonical_name = (
        f"{instrume}_{dt.strftime('%Y%m%d')}_{dt.strftime('%H%M%S')}_{focus_code}.fit"
    )
    canonical_path = os.path.join(os.path.dirname(file_path), canonical_name)
    os.rename(file_path, canonical_path)
    return canonical_path


@get_typer.command(
    help=(
        "Download e-CALLISTO-shaped FITS batches and rename each to the canonical "
        "{INSTRUME}_{YYYYMMDD}_{HHMMSS}_{focus_code}.fit filename."
    )
)
def ecallisto(
    tag: str = typer.Option(..., "--tag", "-t", help="The tag identifying the batches."),
    export: str = typer.Option(
        ...,
        "--export",
        help="Directory to download the renamed e-CALLISTO files into.",
    ),
    focus_code: str = typer.Option(
        ...,
        "--focus-code",
        help="Two-digit focus code (e.g. '02'), used only in the filename suffix.",
    ),
    year: int = typer.Option(None, "--year", "-y", help="Only fetch batches under this year."),
    month: int = typer.Option(None, "--month", "-m", help="Only fetch batches under this month."),
    day: int = typer.Option(None, "--day", "-d", help="Only fetch batches under this day."),
) -> None:
    if not _FOCUS_CODE_RE.match(focus_code):
        typer.secho(
            f"--focus-code must be exactly two decimal digits. Got {focus_code!r}.",
            err=True,
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    params = {"extension": ["fits"], "tag": [tag], "year": year, "month": month, "day": day}
    jsend_dict = safe_request("spectre-data/batches", "GET", params=params)
    endpoints = jsend_dict["data"]

    os.makedirs(export, exist_ok=True)
    for endpoint in endpoints:
        download_path = os.path.join(export, os.path.basename(endpoint))
        response = requests.get(endpoint)
        with open(download_path, "wb") as f:
            f.write(response.content)
        try:
            canonical_path = __rename_to_ecallisto(download_path, focus_code)
        except (ValueError, OSError) as err:
            typer.secho(f"Skipping {os.path.basename(download_path)}: {err}", fg=typer.colors.YELLOW)
            continue
        secho_existing_resource(canonical_path)

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
    export: str = typer.Option(
        None,
        "--export",
        help="Bulk download configs to your local filesystem inside this directory.",
    ),
) -> None:

    jsend_dict = safe_request(f"spectre-data/configs", "GET")
    endpoints = jsend_dict["data"]
    if export is None:
        secho_existing_resources(endpoints)
    else:
        __download_resources(endpoints, export)
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
