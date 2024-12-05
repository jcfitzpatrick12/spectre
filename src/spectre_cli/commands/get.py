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
    FILE_NAME_HELP,
    MODE_HELP
)

get_app = typer.Typer()


@get_app.command()
def callisto_instrument_codes(
) -> None:
    
    jsend_dict = safe_request("get/callisto-instrument-codes",
                              "GET")
    callisto_instrument_codes = jsend_dict["data"]

    for instrument_code in callisto_instrument_codes:
        typer.secho(instrument_code)

    raise typer.Exit()


@get_app.command()
def logs(process_type: str = typer.Option(None, "--process-type", help=PROCESS_TYPE_HELP),
         year: int = typer.Option(None, "--year", "-y", help=YEAR_HELP),
         month: int = typer.Option(None, "--month", "-m", help=MONTH_HELP),
         day: int = typer.Option(None, "--day", "-d", help=DAY_HELP)
) -> None:
    
    payload = {
        "process_type": process_type,
        "year": year,
        "month": month,
        "day": day
    }
    jsend_dict = safe_request("get/logs",
                              "GET",
                              payload)
    file_names = jsend_dict["data"]

    for file_name in file_names:
        typer.secho(file_name)

    raise typer.Exit()


@get_app.command()
def chunk_files(
    tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
    year: int = typer.Option(None, "--year", "-y", help=YEAR_HELP),
    month: int = typer.Option(None, "--month", "-m", help=MONTH_HELP),
    day: int = typer.Option(None, "--day", "-d", help=DAY_HELP),
    extensions: list[str] = typer.Option(None, "--extension", "-e", help=EXTENSIONS_HELP)
) -> None:
    
    payload = {
        "tag": tag,
        "year": year,
        "month": month,
        "day": day,
        "extensions": extensions
    }
    jsend_dict = safe_request("get/chunk-files",
                              "GET",
                              payload)
    file_names = jsend_dict["data"]

    for file_name in file_names:
        typer.secho(file_name)

    raise typer.Exit()


@get_app.command()
def receivers(
) -> None:
    
    jsend_dict = safe_request("get/receivers",
                              "GET")
    receiver_names = jsend_dict["data"]
    
    for receiver_name in receiver_names:
        typer.secho(receiver_name)
        
    raise typer.Exit()


@get_app.command()
def modes(
    receiver_name: str = typer.Option(..., "--receiver", "-r", help=RECEIVER_NAME_HELP)
) -> None:
    
    payload = {
        "receiver_name": receiver_name
    }
    jsend_dict = safe_request("get/modes",
                              "GET",
                              payload)
    receiver_modes = jsend_dict["data"]

    for mode in receiver_modes:
        typer.secho(mode)

    raise typer.Exit()


@get_app.command()
def specifications(
    receiver_name: str = typer.Option(..., "--receiver", "-r", help=RECEIVER_NAME_HELP)
) -> None:
    
    payload = {
        "receiver_name": receiver_name
    }
    jsend_dict = safe_request("get/specifications",
                              "GET",
                              payload)
    specifications = jsend_dict["data"]

    for k, v in specifications.items():
        typer.secho(f"{k}: {v}")

    raise typer.Exit()


@get_app.command()
def fits_configs(
) -> None:
    
    jsend_dict = safe_request("get/fits-configs",
                              "GET")
    file_names = jsend_dict["data"]
    
    if not file_names:
        typer.secho(f"No fits configs found")
    
    else:
        for file_name in file_names:
            typer.secho(file_name)

    raise typer.Exit()


@get_app.command()
def capture_configs(
) -> None:
    
    jsend_dict = safe_request("get/capture-configs",
                              "GET")
    file_names = jsend_dict["data"]
    
    if not file_names:
        typer.secho(f"No capture configs found")
    
    else:
        for file_name in file_names:
            typer.secho(file_name)

    raise typer.Exit()


@get_app.command()
def tags(
    year: int = typer.Option(None, "--year", "-y", help=YEAR_HELP),
    month: int = typer.Option(None, "--month", "-m", help=MONTH_HELP),
    day: int = typer.Option(None, "--day", "-d", help=DAY_HELP),
    
) -> None:
    
    payload = {
        "year": year,
        "month": month,
        "day": day
    }
    jsend_dict = safe_request("get/tags",
                              "GET",
                              payload)
    tags = jsend_dict["data"]

    if not tags:
        typer.secho("No tags found")

    else:
        for tag in tags:
            typer.secho(tag)
    
    raise typer.Exit()

    
@get_app.command()
def log(
    pid: str = typer.Option(None, "--pid", help=PID_HELP),
    file_name: str = typer.Option(None, "--file-name", help=FILE_NAME_HELP)
) -> None:
    
    payload = {
        "pid": pid,
        "file_name": file_name
    }
    jsend_dict = safe_request("get/log",
                              "GET",
                              payload)
    file_contents = jsend_dict["data"]

    typer.secho(file_contents)
    raise typer.Exit()


@get_app.command()
def fits_config_type_template(
    tag: str = typer.Option(None, "--tag", "-t", help=TAG_HELP),
) -> None:
    
    payload = {
        "tag": tag
    }
    jsend_dict = safe_request("get/fits-config-type-template",
                              "GET",
                              payload)
    type_template = jsend_dict["data"]

    for k, v in type_template.items():
        typer.secho(f"{k}: {v}")

    typer.Exit()


@get_app.command()
def capture_config_type_template(
    receiver_name: str = typer.Option(..., "--receiver", "-r", help=RECEIVER_NAME_HELP),
    mode: str = typer.Option(..., "--mode", "-m", help=MODE_HELP),
    tag: str = typer.Option(None, "--tag", "-t", help=TAG_HELP)
) -> None: 
    
    payload = {
        "receiver_name": receiver_name,
        "mode": mode,
        "tag": tag
    }
    jsend_dict = safe_request("get/capture-config-type-template",
                              "GET",
                              payload)
    type_template = jsend_dict["data"]

    for k, v in type_template.items():
        typer.secho(f"{k}: {v}")

    typer.Exit()


@get_app.command()
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
) -> None:
    
    payload = {
        "tag": tag
    }
    jsend_dict = safe_request("get/fits-config",
                              "GET",
                              payload)
    fits_config = jsend_dict["data"]

    for k, v in fits_config.items():
        typer.secho(f"{k}: {v}")

    raise typer.Exit()


@get_app.command()
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
) -> None:
    
    payload = {
        "tag": tag
    }
    jsend_dict = safe_request("get/capture-config",
                              "GET",
                              payload)
    capture_config = jsend_dict["data"]

    for k, v in capture_config.items():
        typer.secho(f"{k}: {v}")

    raise typer.Exit()

    
