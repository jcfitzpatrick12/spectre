# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from typing import List

from spectre.web_fetch.callisto import fetch_chunks

app = typer.Typer()

@app.command()
def callisto(
    instrument_code: str = typer.Option(..., "--instrument-code", "-i", help=""),
    year: int = typer.Option(None, "--year", "-y", help=""),
    month: int = typer.Option(None, "--month", "-m", help=""),
    day: int = typer.Option(None, "--day", "-d", help=""),
) -> None:
    fetch_chunks(instrument_code, year=year, month=month, day=day)
    raise typer.Exit()