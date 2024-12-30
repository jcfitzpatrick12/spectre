# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-

import typer

from ._cli_help import CliHelp
from ._safe_request import safe_request

download_app = typer.Typer(
    help = "Download external spectrogram data."
)

@download_app.command(
        help = ("Download e-Callisto network spectrograms.")
)
def callisto(
    instrument_code: str = typer.Option(..., "--instrument-code", "-i", help=CliHelp.INSTRUMENT_CODE),
    year: int = typer.Option(None, "--year", "-y", help=CliHelp.YEAR),
    month: int = typer.Option(None, "--month", "-m", help=CliHelp.MONTH),
    day: int = typer.Option(None, "--day", "-d", help=CliHelp.DAY),
) -> None:
    json = {
        "instrument_code": instrument_code,
        "year": year,
        "month": month,
        "day": day
    }
    _ = safe_request("callisto/batches",
                     "POST",
                     json = json)
    
    typer.secho(f"Successfully retrieved files for instrument code {instrument_code}")
    raise typer.Exit()