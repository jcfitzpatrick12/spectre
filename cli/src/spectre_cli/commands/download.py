# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-

from typer import Typer, Option, Exit, secho
import os

from spectre_core.config import get_spectre_data_dir_path

from ._safe_request import safe_request

download_typer = Typer(
    help = "Download external spectrogram data."
)

def _secho_downloaded_file(
    rel_path: str
) -> None:
    abs_path = os.path.join(get_spectre_data_dir_path(), rel_path)
    secho(f"Downloaded '{abs_path}'", fg="green")
    
    
def _secho_downloaded_files(
    rel_paths: list[str]
) -> None:    
    for rel_path in rel_paths:
        _secho_downloaded_file(rel_path)
    
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
    rel_paths = jsend_dict["data"]
    _secho_downloaded_files( rel_paths )
    raise Exit()