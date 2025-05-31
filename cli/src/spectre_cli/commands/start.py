# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer

from ._utils import safe_request


start_typer = typer.Typer(help="Start a job.")


@start_typer.command(help="Capture data from an SDR in real time.")
def capture(
    tag: str = typer.Option(..., "--tag", "-t", help="The capture config tag."),
    seconds: int = typer.Option(
        0, "--seconds", help="The seconds component of the capture duration."
    ),
    minutes: int = typer.Option(
        0, "--minutes", help="The minutes component of the capture duration."
    ),
    hours: int = typer.Option(
        0, "--hours", help="The hours component of the capture duration."
    ),
    force_restart: bool = typer.Option(
        False,
        "--force-restart",
        help="When a worker process stops unexpectedly, terminate all workers "
        "and restart.",
    ),
) -> None:
    json = {
        "tag": tag,
        "seconds": seconds,
        "minutes": minutes,
        "hours": hours,
        "force_restart": force_restart,
    }
    _ = safe_request("jobs/capture", "POST", json=json)
    typer.secho(f"Capture completed sucessfully for tag '{tag}'")
    raise typer.Exit()


@start_typer.command(
    help="Capture data from an SDR and post-process it into spectrograms in real time."
)
def session(
    tag: str = typer.Option(..., "--tag", "-t", help="The capture config tag."),
    seconds: int = typer.Option(
        0, "--seconds", help="The seconds component of the session duration."
    ),
    minutes: int = typer.Option(
        0, "--minutes", help="The minutes component of the session duration."
    ),
    hours: int = typer.Option(
        0, "--hours", help="The hours component of the session duration."
    ),
    force_restart: bool = typer.Option(
        False,
        "--force-restart",
        help="When a worker process stops unexpectedly, terminate all workers "
        "and restart.",
    ),
) -> None:
    json = {
        "tag": tag,
        "seconds": seconds,
        "minutes": minutes,
        "hours": hours,
        "force_restart": force_restart,
    }
    _ = safe_request("jobs/session", "POST", json=json)
    typer.secho(f"Session completed sucessfully for tag '{tag}'")
    raise typer.Exit()
