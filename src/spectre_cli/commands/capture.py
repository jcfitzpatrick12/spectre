# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
import requests

from spectre_cli import (
    BASE_URL,
    TAG_HELP,
    SECONDS_HELP,
    MINUTES_HELP,
    HOURS_HELP,
    FORCE_RESTART_HELP
)

app = typer.Typer()

@app.command()
def start(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
          seconds: int = typer.Option(0, "--seconds", help=SECONDS_HELP),
          minutes: int = typer.Option(0, "--minutes", help=MINUTES_HELP),
          hours: int = typer.Option(0, "--hours", help=HOURS_HELP),
          force_restart: bool = typer.Option(False, "--force-restart", help=FORCE_RESTART_HELP)
) -> None:
    payload = {
        "tag": tag,
        "seconds": seconds,
        "minutes": minutes,
        "hours": hours,
        "force_restart": force_restart
    }
    response = requests.post(f"{BASE_URL}/capture/start", json=payload)
    print(response)


@app.command()
def session(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
            seconds: int = typer.Option(0, "--seconds", help=SECONDS_HELP),
            minutes: int = typer.Option(0, "--minutes", help=MINUTES_HELP),
            hours: int = typer.Option(0, "--hours", help=HOURS_HELP),
            force_restart: bool = typer.Option(False, "--force-restart", help=FORCE_RESTART_HELP)
) -> None:
    # capture.session(tag,
    #                 seconds = seconds,
    #                 minutes = minutes,
    #                 hours = hours,
    #                 force_restart = force_restart)
    raise typer.Exit()

