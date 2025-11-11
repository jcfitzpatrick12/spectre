# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-

import typer

from ._utils import safe_request, spinner
from ._secho_resources import secho_new_resources


download_typer = typer.Typer(help="Download external spectrogram data.")


@download_typer.command(help="Download e-Callisto network spectrogram data.")
def callisto(
    instrument_codes: list[str] = typer.Option(
        ...,
        "--instrument-code",
        "-i",
        help="The case-sensitive e-Callisto station instrument code.",
    ),
    year: int = typer.Option(
        ..., "--year", "-y", help="Download files under this year."
    ),
    month: int = typer.Option(
        ..., "--month", "-m", help="Download files under this month."
    ),
    day: int = typer.Option(..., "--day", "-d", help="Download files under this day."),
) -> None:
    json = {
        "instrument_codes": instrument_codes,
        "year": year,
        "month": month,
        "day": day,
    }
    with spinner():
        jsend_dict = safe_request(f"callisto/batches", "POST", json=json)
    endpoints = jsend_dict["data"]
    secho_new_resources(endpoints)
    raise typer.Exit()
