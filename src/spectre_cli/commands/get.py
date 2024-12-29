# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
import yaml

from spectre_cli.commands import safe_request
from spectre_cli.commands import CliHelp

get_app = typer.Typer(
    help = "Display one or many resources."
)

def pprint_dict(d: dict):
    print( yaml.dump(d, sort_keys=True, default_flow_style=False) )

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
def logs(process_type: str = typer.Option(None, "--process-type", help=CliHelp.PROCESS_TYPE),
         year: int = typer.Option(None, "--year", "-y", help=CliHelp.YEAR),
         month: int = typer.Option(None, "--month", "-m", help=CliHelp.MONTH),
         day: int = typer.Option(None, "--day", "-d", help=CliHelp.DAY)
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
    tag: list[str] = typer.Option([], "--tag", "-t", help=CliHelp.TAG),
    year: int = typer.Option(None, "--year", "-y", help=CliHelp.YEAR),
    month: int = typer.Option(None, "--month", "-m", help=CliHelp.MONTH),
    day: int = typer.Option(None, "--day", "-d", help=CliHelp.DAY),
    extensions: list[str] = typer.Option(None, "--extension", "-e", help=CliHelp.EXTENSIONS)
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
    receiver_name: str = typer.Option(..., "--receiver", "-r", help=CliHelp.RECEIVER_NAME)
) -> None:
    
    jsend_dict = safe_request(f"receivers/{receiver_name}/modes",
                              "GET")
    receiver_modes = jsend_dict["data"]

    for receiver_mode in receiver_modes:
        typer.secho(receiver_mode)

    raise typer.Exit()


@get_app.command(
        help = ("Print receiver hardware specifications.")
)
def specs(
    receiver_name: str = typer.Option(..., "--receiver", "-r", help=CliHelp.RECEIVER_NAME)
) -> None:
    
    params = {
        "receiver_name": receiver_name
    }
    jsend_dict = safe_request(f"receivers/{receiver_name}/specs",
                              "GET",
                              params = params)
    specs = jsend_dict["data"]

    for k, v in specs.items():
        typer.secho(f"{k}: {v}")

    raise typer.Exit()


@get_app.command(
        help = ("List defined capture configs.")
)
def capture_configs(
) -> None:
    
    jsend_dict = safe_request(f"spectre-data/capture-configs",
                              "GET")
    file_names = jsend_dict["data"]
    
    for file_name in file_names:
        typer.secho(file_name)

    raise typer.Exit()


@get_app.command(
        help = ("Print capture config file contents.")
)
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=CliHelp.TAG),
) -> None:
    jsend_dict = safe_request(f"spectre-data/capture-configs/{tag}",
                              "GET")
    capture_config = jsend_dict["data"]

    pprint_dict(capture_config)

    raise typer.Exit()


@get_app.command(
        help = ("List tags with existing chunk files.")
)
def tags(
    year: int = typer.Option(None, "--year", "-y", help=CliHelp.YEAR),
    month: int = typer.Option(None, "--month", "-m", help=CliHelp.MONTH),
    day: int = typer.Option(None, "--day", "-d", help=CliHelp.DAY),
    
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

    for tag in tags:
        typer.secho(tag)
    
    raise typer.Exit()

    
@get_app.command(
        help = ("Print log file contents.")
)
def log(
    pid: str = typer.Option(..., "--pid", help=CliHelp.PID),
) -> None:
    
    jsend_dict = safe_request(f"spectre-data/logs/{pid}",
                              "GET")
    file_contents = jsend_dict["data"]

    typer.secho(file_contents)
    raise typer.Exit()


@get_app.command(
        help = ("Print a capture template.")
)
def capture_template(
    receiver_name: str = typer.Option(..., "--receiver", "-r", help=CliHelp.RECEIVER_NAME),
    receiver_mode: str = typer.Option(..., "--mode", "-m", help=CliHelp.MODE),
    param_name: str = typer.Option(None, "--param", "-p", help=CliHelp.PARAMETER_NAME)
) -> None: 
    
    params = {
        "receiver_mode": receiver_mode,
    }
    jsend_dict = safe_request(f"receivers/{receiver_name}/capture-template",
                              "GET",
                              params = params)
    capture_template = jsend_dict["data"]

    if param_name is None:
        pprint_dict(capture_template)
    else:
        if param_name not in capture_template:
            raise KeyError(f"A parameter with name '{param_name}' does not exist "
                        f"in the capture template for the receiver '{receiver_name}' "
                        f"operating in mode '{receiver_mode}'. Expected one of: "
                        f"{list(capture_template.keys())}")
        pprint_dict(capture_template[param_name])

    typer.Exit()


    
