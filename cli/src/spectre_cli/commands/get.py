# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typer import Typer, Option, Exit, secho

from ._safe_request import safe_request
from ._shared import pprint_dict


get_typer = Typer(
    help = "Display one or many resources."
)

def _secho_file(
    abs_path: str
) -> None:
    secho(abs_path)
    
    
def _secho_files(
    abs_paths: list[str]
) -> None:    
    for abs_path in abs_paths:
        _secho_file(abs_path)
        

@get_typer.command(
    help = "List supported e-Callisto instrument codes."
)
def callisto_instrument_codes(
) -> None:
    jsend_dict = safe_request("callisto/instrument-codes",
                              "GET")
    callisto_instrument_codes = jsend_dict["data"]

    for instrument_code in callisto_instrument_codes:
        secho(instrument_code)

    raise Exit()


@get_typer.command(
    help = "List existing log files."
)
def logs(process_type: str = Option(None, 
                                    "--process-type", 
                                    help="Specifies one of 'worker' or 'user'."),
         year: int = Option(None, 
                            "--year", 
                            "-y", 
                            help="Filter for log files under this numeric year."),
         month: int = Option(None, 
                             "--month", 
                             "-m", 
                             help="Filter for log files under this numeric month."),
         day: int = Option(None, 
                           "--day", 
                           "-d", 
                           help="Filter for log files under this numeric day.")
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
    abs_paths = jsend_dict["data"]

    _secho_files(abs_paths)
    raise Exit()


@get_typer.command(
    help = "List existing batch files."
)
def batch_files(
    tag: str = Option(..., 
                    "--tag", 
                    "-t", 
                    help="The tag used to capture the data."),
    year: int = Option(None, 
                       "--year", 
                       "-y", 
                       help="Filter for batch files under this numeric year."),
    month: int = Option(None, 
                        "--month", 
                        "-m", 
                        help="Filter for batch files under this numeric month."),
    day: int = Option(None, 
                      "--day", 
                      "-d", 
                      help="Filter for batch files under this numeric day."),
    extensions: list[str] = Option(None, 
                                   "--extension", 
                                   "-e", 
                                   help="Filter for batch files with this file extension.")
) -> None:
    
    params = {
        "year": year,
        "month": month,
        "day": day,
        "extension": extensions
    }
    jsend_dict = safe_request(f"spectre-data/batches/{tag}",
                              "GET",
                              params = params)
    abs_paths = jsend_dict["data"]

    _secho_files(abs_paths)
    raise Exit()


@get_typer.command(
    help = "List supported receivers."
)
def receivers(
) -> None:
    
    jsend_dict = safe_request("receivers",
                              "GET")
    receiver_names = jsend_dict["data"]
    
    for receiver_name in receiver_names:
        secho(receiver_name)
        
    raise Exit()


@get_typer.command(
    help = ("List the supported operating modes for a receiver.")
)
def modes(
    receiver_name: str = Option(..., 
                                "--receiver", 
                                "-r", 
                                help="The name of the receiver.")
) -> None:
    
    jsend_dict = safe_request(f"receivers/{receiver_name}/modes",
                              "GET")
    receiver_modes = jsend_dict["data"]

    for receiver_mode in receiver_modes:
        secho(receiver_mode)
        
    raise Exit()


@get_typer.command(
    help = "Print receiver hardware specifications."
)
def specs(
    receiver_name: str = Option(..., 
                                "--receiver", 
                                "-r", 
                                help="The name of the receiver.")
) -> None:
    
    params = {
        "receiver_name": receiver_name
    }
    jsend_dict = safe_request(f"receivers/{receiver_name}/specs",
                              "GET",
                              params = params)
    specs = jsend_dict["data"]

    for k, v in specs.items():
        secho(f"{k}: {v}")

    raise Exit()


@get_typer.command(
    help = "List existing capture configs."
)
def capture_configs(
) -> None:
    
    jsend_dict = safe_request(f"spectre-data/configs",
                              "GET")
    abs_paths = jsend_dict["data"]
    
    _secho_files(abs_paths)

    raise Exit()


@get_typer.command(
    help = "Print capture config file contents."
)
def capture_config(tag: str = Option(..., 
                                     "--tag", 
                                     "-t", 
                                     help="Unique identifier for the capture config."),
) -> None:
    jsend_dict = safe_request(f"spectre-data/configs/{tag}",
                              "GET")
    capture_config = jsend_dict["data"]

    pprint_dict(capture_config)

    raise Exit()


@get_typer.command(
    help = "List tags with existing batch files."
)
def tags(
    year: int = Option(None, 
                       "--year", 
                       "-y", 
                       help="Find tags with existing batch files under this numeric year."),
    month: int = Option(None, 
                        "--month", 
                        "-m", 
                        help="Find tags with existing batch files under this numeric month."),
    day: int = Option(None, 
                      "--day", 
                      "-d", 
                      help="Find tags with existing batch files under this numeric day."),
    
) -> None:
    params = {
        "year": year,
        "month": month,
        "day": day
    }
    jsend_dict = safe_request("spectre-data/batches/tags",
                              "GET",
                              params = params)
    tags = jsend_dict["data"]

    for tag in tags:
        secho(tag)
    
    raise Exit()

    
@get_typer.command(
        help = "Print log file contents."
)
def log(
    pid: str = Option(..., 
                      "--pid", 
                      help="The process ID."),
) -> None:
    
    jsend_dict = safe_request(f"spectre-data/logs/{pid}",
                              "GET")
    file_contents = jsend_dict["data"]

    secho(file_contents)
    raise Exit()


@get_typer.command(
        help = "Print a capture template."
)
def capture_template(
    receiver_name: str = Option(..., 
                                "--receiver", 
                                "-r", 
                                help="The name of the receiver."),
    receiver_mode: str = Option(..., 
                                "--mode", 
                                "-m", 
                                help="The operating mode of the receiver."),
    param_name: str = Option(None, 
                             "--param", 
                             "-p", 
                             help="Filter for a particular parameter template.")
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

    Exit()


    
