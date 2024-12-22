# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer

from spectre_cli.commands import safe_request
from spectre_cli.commands import CliHelp

start_app = typer.Typer(
    help = "Start a job."
)

@start_app.command(
        help = ("Start a capture.")
)
def capture(tag: str = typer.Option(..., "--tag", "-t", help=CliHelp.TAG),
            seconds: int = typer.Option(0, "--seconds", help=CliHelp.SECONDS),
            minutes: int = typer.Option(0, "--minutes", help=CliHelp.MINUTES),
            hours: int = typer.Option(0, "--hours", help=CliHelp.HOURS),
            force_restart: bool = typer.Option(False, "--force-restart", help=CliHelp.FORCE_RESTART)
) -> None:
    json = {
        "tag": tag,
        "seconds": seconds,
        "minutes": minutes,
        "hours": hours,
        "force_restart": force_restart
    }
    _ = safe_request("jobs/capture", 
                     "POST", 
                     json = json)
    typer.secho(f"Capture completed sucessfully for tag '{tag}'")
    raise typer.Exit()

@start_app.command(
        help = ("Start a session.")
)
def session(tag: str = typer.Option(..., "--tag", "-t", help=CliHelp.TAG),
            seconds: int = typer.Option(0, "--seconds", help=CliHelp.SECONDS),
            minutes: int = typer.Option(0, "--minutes", help=CliHelp.MINUTES),
            hours: int = typer.Option(0, "--hours", help=CliHelp.HOURS),
            force_restart: bool = typer.Option(False, "--force-restart", help=CliHelp.FORCE_RESTART)
) -> None:
    json = {
        "tag": tag,
        "seconds": seconds,
        "minutes": minutes,
        "hours": hours,
        "force_restart": force_restart
    }
    _ = safe_request("jobs/session", 
                     "POST", 
                     json = json)
    typer.secho(f"Session completed sucessfully for tag '{tag}'")
    raise typer.Exit()


