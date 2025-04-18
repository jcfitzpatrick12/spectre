# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-

from typer import Typer, Option, Exit, secho

from ._safe_request import safe_request

download_typer = Typer(
    help = "Download external spectrogram data."
)

def _secho_downloaded_resource(
    resource_endpoint: str
) -> None:
    secho(resource_endpoint, fg="green")
    
    
def _secho_downloaded_resources(
    resource_endpoints: list[str]
) -> None:    
    for resource_endpoint in resource_endpoints:
        _secho_downloaded_resource(resource_endpoint)


@download_typer.command(
    help = "Download e-Callisto network spectrogram data."
)
def callisto(
    instrument_code: str = Option(..., 
                                  "--instrument-code", 
                                  "-i", 
                                  help="The case-sensitive e-Callisto station instrument codes."),
    year: int = Option(None, 
                       "--year", 
                       "-y", 
                       help="Download files under this numeric year."),
    month: int = Option(None, 
                        "--month", 
                        "-m", 
                        help="Download files under this numeric month."),
    day: int = Option(None, 
                      "--day", 
                      "-d", 
                      help="Download files under this numeric day."),
) -> None:
    json = {
        "instrument_code": instrument_code,
        "year": year,
        "month": month,
        "day": day
    }
    secho(f"Download in progress...", fg="yellow")
    jsend_dict = safe_request("callisto/batches",
                              "POST",
                              json=json)
    resource_endpoints = jsend_dict["data"]
    _secho_downloaded_resources( resource_endpoints )
    raise Exit()
