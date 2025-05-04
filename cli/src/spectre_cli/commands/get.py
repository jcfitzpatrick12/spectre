# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typer import Typer, Option, Exit, secho

from ._utils import safe_request, build_date_path
from ._secho_resources import pprint_dict, secho_existing_resources



get_typer = Typer(
    help = "Display one or many resources."
)
        

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
def logs(
   process_types: list[str] = Option([], 
                               "--process-type", 
                               help="Specifies one of 'worker' or 'user'."),
   year: int = Option(None, 
                      "--year", 
                      "-y", 
                      help="List log files under this numeric year."),
   month: int = Option(None, 
                       "--month", 
                       "-m", 
                       help="List log files under this numeric month."),
   day: int = Option(None, 
                     "--day", 
                     "-d", 
                     help="List log files under this numeric day."),

) -> None:
    params = {
        "process_type": process_types,
    }
    jsend_dict = safe_request(f"spectre-data/logs/{build_date_path(year, month, day)}",
                              "GET",
                              params = params)
    endpoints = jsend_dict["data"]

    secho_existing_resources(endpoints)
    raise Exit()


@get_typer.command(
    help = "Print the contents of a log file."
)
def log(
    year: int = Option(..., 
                       "--year", 
                       "-y", 
                       help="Read a log file under this numeric year."),
    month: int = Option(..., 
                        "--month", 
                        "-m", 
                        help="Read a log file under this numeric month."),
    day: int = Option(..., 
                      "--day", 
                      "-d", 
                      help="Read a log file under this numeric day."),
    file_name: str = Option(...,
                            "-f",
                            help="The file name of the log file.")
) -> None:
    jsend_dict = safe_request(f"spectre-data/logs/{year}/{month}/{day}/{file_name}/raw",
                              "GET")
    log_contents = jsend_dict["data"]
    print( log_contents )
    raise Exit()


@get_typer.command(
    help = "List existing batch files."
)
def batch_files(
    extensions: list[str] = Option([], 
                                   "--extension", 
                                   "-e", 
                                   help="Filter for batch files with this file extension."),
    tags: list[str] = Option([], 
                            "--tag", 
                            "-t", 
                            help="Filter batch files with this tag."),
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
                      help="Filter for batch files under this numeric day.")
) -> None:
    params = {
        "extension": extensions,
        "tag": tags
    }
    jsend_dict = safe_request(f"spectre-data/batches/{build_date_path(year, month, day)}",
                              "GET",
                              params = params)
    endpoints = jsend_dict["data"]

    secho_existing_resources(endpoints)
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
    endpoints = jsend_dict["data"]
    secho_existing_resources(endpoints)
    raise Exit()


@get_typer.command(
    help = "Print capture config file contents."
)
def capture_config(
    base_file_name: str = Option(None, 
                                 "-f", 
                                 help="The base file name of the capture config"),
    tag: str = Option(None,
                      "--tag",
                      "-t",
                      help="The unique identifier for the capture config")
) -> None:

    if not (base_file_name is None) ^ (tag is None):
        raise ValueError("Specify either the tag or file name, not both.")

    base_file_name = base_file_name or f"{tag}.json"
    
    jsend_dict = safe_request(f"spectre-data/configs/{base_file_name}/raw",
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
    url = f"spectre-data/batches/{build_date_path(year, month, day)}/tags" if year is not None else "spectre-data/batches/tags"
    jsend_dict = safe_request(url,
                              "GET")
    tags = jsend_dict["data"]

    for tag in tags:
        secho(tag)
    
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


    
