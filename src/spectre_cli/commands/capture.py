# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer

from spectre_cli.commands import safe_request
from spectre_cli.commands import (
    TAG_HELP,
    SECONDS_HELP,
    MINUTES_HELP,
    HOURS_HELP,
    FORCE_RESTART_HELP
)

capture_app = typer.Typer()

@capture_app.command()
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
    _ = safe_request("capture/start", 
                     "POST", 
                     payload)
    typer.secho(f"Capture completed sucessfully for tag '{tag}'", fg = "green")
    raise typer.Exit()

@capture_app.command()
def session(tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
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
    _ = safe_request("capture/session", 
                     "POST", 
                     payload)
    typer.secho(f"Capture session completed sucessfully for tag '{tag}'", fg = "green")
    raise typer.Exit()


