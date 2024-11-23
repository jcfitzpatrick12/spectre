# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from typing import List

from host.services import capture
from host.cli import (
    RECEIVER_NAME_HELP,
    MODE_HELP,
    TAG_HELP,
    SECONDS_HELP,
    MINUTES_HELP,
    HOURS_HELP,
    FORCE_RESTART_HELP
)

app = typer.Typer()


@app.command()
def session(tags: List[str] = typer.Option(..., "--tag", "-t", help=TAG_HELP),
            seconds: int = typer.Option(0, "--seconds", help=SECONDS_HELP),
            minutes: int = typer.Option(0, "--minutes", help=MINUTES_HELP),
            hours: int = typer.Option(0, "--hours", help=HOURS_HELP),
            force_restart: bool = typer.Option(False, "--force-restart", help=FORCE_RESTART_HELP)
) -> None:
    capture.session(tags,
                    seconds = seconds,
                    minutes = minutes,
                    hours = hours,
                    force_restart = force_restart)
    raise typer.Exit()


@app.command()
def start(tags: List[str] = typer.Option(..., "--tag", "-t", help=TAG_HELP),
          seconds: int = typer.Option(0, "--seconds", help=SECONDS_HELP),
          minutes: int = typer.Option(0, "--minutes", help=MINUTES_HELP),
          hours: int = typer.Option(0, "--hours", help=HOURS_HELP),
          force_restart: bool = typer.Option(False, "--force-restart", help=FORCE_RESTART_HELP)
) -> None:
    capture.start(tags,
                  seconds = seconds,
                  minutes = minutes,
                  hours = hours,
                  force_restart = force_restart)
    raise typer.Exit()


# @app.command()
# def analytical_test(
#     test_tag: str = typer.Option(..., "--tag", "-t", help="Tag for the analytical test"),
#     show_slice_status: bool = typer.Option(False, "--show-slice-status", help="If partial success, print the times of the spectral slices which failed validation")
# ) -> None: 
#     do_analytical_test.main(test_tag, show_slice_status = show_slice_status)
#     raise typer.Exit()

