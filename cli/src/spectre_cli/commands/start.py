# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer

from ._utils import safe_request


start_typer = typer.Typer(help="Start a job.")

_DEFAULT_DURATION = 0
_DEFAULT_MAX_RESTARTS = 5
_DEFAULT_FORCE_RESTART = False
_DEFAULT_SKIP_VALIDATION = False


@start_typer.command(help="Capture data from an SDR in real time.")
def capture(
    tag: str = typer.Option(..., "--tag", "-t", help="The capture config tag."),
    seconds: int = typer.Option(
        _DEFAULT_DURATION,
        "--seconds",
        help="The seconds component of the job duration.",
    ),
    minutes: int = typer.Option(
        _DEFAULT_DURATION,
        "--minutes",
        help="The minutes component of the job duration.",
    ),
    hours: int = typer.Option(
        _DEFAULT_DURATION,
        "--hours",
        help="The hours component of the job duration.",
    ),
    force_restart: bool = typer.Option(
        _DEFAULT_FORCE_RESTART,
        "--force-restart",
        help="If specified, restart all workers if one dies unexpectedly.",
    ),
    max_restarts: int = typer.Option(
        _DEFAULT_MAX_RESTARTS,
        "--max-restarts",
        help="Maximum number of times workers can be restarted before giving up and killing all workers.",
    ),
    skip_validation: bool = typer.Option(
        _DEFAULT_SKIP_VALIDATION,
        "--skip-validation",
        help="If specified, do not validate parameters.",
    ),
) -> None:
    json = {
        "tag": tag,
        "seconds": seconds,
        "minutes": minutes,
        "hours": hours,
        "force_restart": force_restart,
        "max_restarts": max_restarts,
        "validate": not skip_validation,
    }
    _ = safe_request("jobs/capture", "POST", json=json)
    typer.secho(f"Capture completed successfully for tag '{tag}'")
    raise typer.Exit()


@start_typer.command(
    help="Capture data from an SDR and post-process it into spectrograms in real time."
)
def session(
    tag: str = typer.Option(..., "--tag", "-t", help="The capture config tag."),
    seconds: int = typer.Option(
        _DEFAULT_DURATION,
        "--seconds",
        help="The seconds component of the job duration.",
    ),
    minutes: int = typer.Option(
        _DEFAULT_DURATION,
        "--minutes",
        help="The minutes component of the job duration.",
    ),
    hours: int = typer.Option(
        _DEFAULT_DURATION,
        "--hours",
        help="The hours component of the job duration.",
    ),
    force_restart: bool = typer.Option(
        _DEFAULT_FORCE_RESTART,
        "--force-restart",
        help="If specified, restart all workers if one dies unexpectedly.",
    ),
    max_restarts: int = typer.Option(
        _DEFAULT_MAX_RESTARTS,
        "--max-restarts",
        help="Maximum number of times workers can be restarted before giving up and killing all workers.",
    ),
    skip_validation: bool = typer.Option(
        _DEFAULT_SKIP_VALIDATION,
        "--skip-validation",
        help="If specified, do not validate parameters.",
    ),
) -> None:
    json = {
        "tag": tag,
        "seconds": seconds,
        "minutes": minutes,
        "hours": hours,
        "force_restart": force_restart,
        "max_restarts": max_restarts,
        "validate": not skip_validation,
    }
    _ = safe_request("jobs/session", "POST", json=json)
    typer.secho(f"Session completed successfully for tag '{tag}'")
    raise typer.Exit()
