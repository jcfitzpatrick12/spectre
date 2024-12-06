# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-

import typer

from spectre_cli.commands import safe_request
from spectre_cli.commands import(
    YEAR_HELP,
    MONTH_HELP,
    DAY_HELP,
    INSTRUMENT_CODE_HELP
)

download_app = typer.Typer()

@download_app.command()
def callisto(
    instrument_code: str = typer.Option(..., "--instrument-code", "-i", help=INSTRUMENT_CODE_HELP),
    year: int = typer.Option(None, "--year", "-y", help=YEAR_HELP),
    month: int = typer.Option(None, "--month", "-m", help=MONTH_HELP),
    day: int = typer.Option(None, "--day", "-d", help=DAY_HELP),
) -> None:
    json = {
        "instrument_code": instrument_code,
        "year": year,
        "month": month,
        "day": day
    }
    _ = safe_request("callisto/chunks",
                     "POST",
                     json = json)
    
    typer.secho(f"Successfully retrieved files for instrument code {instrument_code}")
    raise typer.Exit()