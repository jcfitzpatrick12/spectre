# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from typing import List

from host.services import test
from host.cli import (
    TAG_HELP,
    SECONDS_HELP,
    MINUTES_HELP,
    HOURS_HELP
)

app = typer.Typer()


@app.command()
def end_to_end(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
               seconds: int = typer.Option(0, "--seconds", help=SECONDS_HELP),
               minutes: int = typer.Option(0, "--minutes", help=MINUTES_HELP),
               hours: int = typer.Option(0, "--hours", help=HOURS_HELP)
) -> None:
    test.end_to_end(tag,
                    seconds = seconds,
                    minutes = minutes,
                    hours = hours)
    raise typer.Exit()