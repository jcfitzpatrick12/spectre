# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer

from spectre_cli.commands import safe_request
from spectre_cli.commands import (
    PROCESS_TYPE_HELP,
    YEAR_HELP,
    MONTH_HELP,
    DAY_HELP,
    TAG_HELP,
    EXTENSIONS_HELP,
    RECEIVER_NAME_HELP,
    PID_HELP,
    MODE_HELP
)

get_app = typer.Typer()


@get_app.command(
        help = ("List defined e-Callisto instrument codes.")
)
def callisto_instrument_codes(
) -> None:
    
    jsend_dict = safe_request("callisto/instrument-codes",
                              "GET")
    callisto_instrument_codes = jsend_dict["data"]

    for instrument_code in callisto_instrument_codes:
        typer.secho(instrument_code)

    raise typer.Exit()


@get_app.command(
        help = ("List existing log files.")
)
def logs(process_type: str = typer.Option(None, "--process-type", help=PROCESS_TYPE_HELP),
         year: int = typer.Option(None, "--year", "-y", help=YEAR_HELP),
         month: int = typer.Option(None, "--month", "-m", help=MONTH_HELP),
         day: int = typer.Option(None, "--day", "-d", help=DAY_HELP)
) -> None:
    
    params = {
        "process-type": process_type,
        "year": year,
        "month": month,
        "day": day
    }
    jsend_dict = safe_request("spectre-data/logs",
                              "GET",
                              params = params)
    file_names = jsend_dict["data"]

    for file_name in file_names:
        typer.secho(file_name)

    raise typer.Exit()


@get_app.command(
        help = ("List existing chunk files.")
)
def chunk_files(
    tag: list[str] = typer.Option([], "--tag", "-t", help=TAG_HELP),
    year: int = typer.Option(None, "--year", "-y", help=YEAR_HELP),
    month: int = typer.Option(None, "--month", "-m", help=MONTH_HELP),
    day: int = typer.Option(None, "--day", "-d", help=DAY_HELP),
    extensions: list[str] = typer.Option(None, "--extension", "-e", help=EXTENSIONS_HELP)
) -> None:
    
    params = {
        "tag": tag,
        "year": year,
        "month": month,
        "day": day,
        "extension": extensions
    }
    jsend_dict = safe_request("spectre-data/chunks",
                              "GET",
                              params = params)
    file_names = jsend_dict["data"]

    for file_name in file_names:
        typer.secho(file_name)

    raise typer.Exit()


@get_app.command(
        help = ("List defined receivers.")
)
def receivers(
) -> None:
    
    jsend_dict = safe_request("receivers",
                              "GET")
    receiver_names = jsend_dict["data"]
    
    for receiver_name in receiver_names:
        typer.secho(receiver_name)
        
    raise typer.Exit()


@get_app.command(
        help = ("List defined receiver modes.")
)
def modes(
    receiver_name: str = typer.Option(..., "--receiver", "-r", help=RECEIVER_NAME_HELP)
) -> None:
    
    jsend_dict = safe_request(f"receivers/{receiver_name}/modes",
                              "GET")
    receiver_modes = jsend_dict["data"]

    for mode in receiver_modes:
        typer.secho(mode)

    raise typer.Exit()


@get_app.command(
        help = ("Print receiver hardware specifications.")
)
def specifications(
    receiver_name: str = typer.Option(..., "--receiver", "-r", help=RECEIVER_NAME_HELP)
) -> None:
    
    params = {
        "receiver_name": receiver_name
    }
    jsend_dict = safe_request(f"receivers/{receiver_name}/specifications",
                              "GET",
                              params = params)
    specifications = jsend_dict["data"]

    for k, v in specifications.items():
        typer.secho(f"{k}: {v}")

    raise typer.Exit()


@get_app.command(
        help = ("List defined fits configs.")
)
def fits_configs(
) -> None:
    
    jsend_dict = safe_request(f"spectre-data/configs/fits",
                              "GET")
    file_names = jsend_dict["data"]
    
    if not file_names:
        typer.secho(f"No fits configs found")
    
    else:
        for file_name in file_names:
            typer.secho(file_name)

    raise typer.Exit()


@get_app.command(
        help = ("List defined capture configs.")
)
def capture_configs(
) -> None:
    
    jsend_dict = safe_request(f"spectre-data/configs/capture",
                              "GET")
    file_names = jsend_dict["data"]
    
    if not file_names:
        typer.secho(f"No capture configs found")
    
    else:
        for file_name in file_names:
            typer.secho(file_name)

    raise typer.Exit()


@get_app.command(
        help = ("List tags with existing chunk files.")
)
def tags(
    year: int = typer.Option(None, "--year", "-y", help=YEAR_HELP),
    month: int = typer.Option(None, "--month", "-m", help=MONTH_HELP),
    day: int = typer.Option(None, "--day", "-d", help=DAY_HELP),
    
) -> None:
    
    params = {
        "year": year,
        "month": month,
        "day": day
    }
    jsend_dict = safe_request("spectre-data/chunks/tags",
                              "GET",
                              params = params)
    tags = jsend_dict["data"]

    if not tags:
        typer.secho("No tags found")

    else:
        for tag in tags:
            typer.secho(tag)
    
    raise typer.Exit()

    
@get_app.command(
        help = ("Print log file contents.")
)
def log(
    pid: str = typer.Option(None, "--pid", help=PID_HELP),
) -> None:
    
    jsend_dict = safe_request(f"spectre-data/logs/{pid}",
                              "GET")
    file_contents = jsend_dict["data"]

    typer.secho(file_contents)
    raise typer.Exit()


@get_app.command(
        help = ("Print the capture config type template.")
)
def type_template(
    receiver_name: str = typer.Option(..., "--receiver", "-r", help=RECEIVER_NAME_HELP),
    mode: str = typer.Option(..., "--mode", "-m", help=MODE_HELP),
) -> None: 
    
    params = {
        "mode": mode,
    }
    jsend_dict = safe_request(f"receivers/{receiver_name}/type-template",
                              "GET",
                              params = params)
    type_template = jsend_dict["data"]

    for k, v in type_template.items():
        typer.secho(f"{k}: {v}")

    typer.Exit()


@get_app.command(
        help = ("Print fits config file contents.")
)
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
) -> None:
    
    jsend_dict = safe_request(f"spectre-data/configs/fits/{tag}",
                              "GET")
    fits_config = jsend_dict["data"]

    for k, v in fits_config.items():
        typer.secho(f"{k}: {v}")

    raise typer.Exit()


@get_app.command(
        help = ("Print capture config file contents")
)
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
) -> None:
    
    jsend_dict = safe_request(f"spectre-data/configs/capture/{tag}",
                              "GET")
    capture_config = jsend_dict["data"]

    for k, v in capture_config.items():
        typer.secho(f"{k}: {v}")

    raise typer.Exit()

    
