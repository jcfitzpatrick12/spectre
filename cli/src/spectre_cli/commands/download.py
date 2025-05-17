# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-

from typer import Typer, Option, Exit, secho

from ._utils import safe_request, build_date_path
from ._secho_resources import secho_new_resources


download_typer = Typer(
    help = "Download external spectrogram data."
)


@download_typer.command(
    help = "Download e-Callisto network spectrogram data."
)
def callisto(
    instrument_codes: list[str] = Option(..., 
                                        "--instrument-code", 
                                        "-i", 
                                        help="The case-sensitive e-Callisto station instrument code."),
    year: int = Option(..., 
                       "--year", 
                       "-y", 
                       help="Download files under this numeric year."),
    month: int = Option(..., 
                        "--month", 
                        "-m", 
                        help="Download files under this numeric month."),
    day: int = Option(..., 
                      "--day", 
                      "-d", 
                      help="Download files under this numeric day."),
) -> None:
    json = {
        "instrument_codes": instrument_codes,
    }
    secho(f"Download in progress...", fg="yellow")
    jsend_dict = safe_request(f"callisto/batches/{build_date_path(year, month, day)}",
                              "POST",
                              json=json)
    endpoints = jsend_dict["data"]
    secho_new_resources( endpoints )
    raise Exit()
