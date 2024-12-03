# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-

import typer

from spectre_cli.commands import(
    YEAR_HELP,
    MONTH_HELP,
    DAY_HELP,
    INSTRUMENT_CODE_HELP
)

app = typer.Typer()

@app.command()
def callisto(
    instrument_code: str = typer.Option(..., "--instrument-code", "-i", help=INSTRUMENT_CODE_HELP),
    year: int = typer.Option(None, "--year", "-y", help=YEAR_HELP),
    month: int = typer.Option(None, "--month", "-m", help=MONTH_HELP),
    day: int = typer.Option(None, "--day", "-d", help=DAY_HELP),
) -> None:
    # web_fetch.callisto(instrument_code, year, month, day)
    raise typer.Exit()