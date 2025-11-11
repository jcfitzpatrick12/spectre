# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer

from ._utils import safe_request, spinner


record_typer = typer.Typer(help="Start recording data.")

_DEFAULT_MAX_RESTARTS = 5
_DEFAULT_FORCE_RESTART = False
_DEFAULT_SKIP_VALIDATION = False


@record_typer.command(help="Capture data from an SDR in real time.")
def signal(
    tags: list[str] = typer.Option(..., "--tag", "-t", help="The config tag."),
    duration: float = typer.Option(
        ...,
        "--duration", "-d",
        help="How long to record the signal for, in seconds.",
    ),
    force_restart: bool = typer.Option(
        _DEFAULT_FORCE_RESTART,
        "--force-restart",
        help="If specified, restart if an error occurs at runtime.",
    ),
    max_restarts: int = typer.Option(
        _DEFAULT_MAX_RESTARTS,
        "--max-restarts",
        help="Maximum number of times to restart before giving up.",
    ),
    skip_validation: bool = typer.Option(
        _DEFAULT_SKIP_VALIDATION,
        "--skip-validation",
        help="If specified, do not validate config parameters.",
    ),
) -> None:
    json = {
        "tags": tags,
        "duration": duration,
        "force_restart": force_restart,
        "max_restarts": max_restarts,
        "validate": not skip_validation,
    }
    with spinner():
        _ = safe_request("recordings/signal", "POST", json=json)
    raise typer.Exit()


@record_typer.command(
    help="Capture data from an SDR and post-process it into spectrograms in real time."
)
def spectrograms(
    tags: list[str] = typer.Option(..., "--tag", "-t", help="The config tag."),
    duration: float = typer.Option(
        ...,
        "--duration", "-d",
        help="How long to record the signal for, in seconds.",
    ),
    force_restart: bool = typer.Option(
        _DEFAULT_FORCE_RESTART,
        "--force-restart",
        help="If specified, restart if an error occurs at runtime.",
    ),
    max_restarts: int = typer.Option(
        _DEFAULT_MAX_RESTARTS,
        "--max-restarts",
        help="Maximum number of times to restart before giving up.",
    ),
    skip_validation: bool = typer.Option(
        _DEFAULT_SKIP_VALIDATION,
        "--skip-validation",
        help="If specified, do not validate config parameters.",
    ),
) -> None:
    json = {
        "tags": tags,
        "duration": duration,
        "force_restart": force_restart,
        "max_restarts": max_restarts,
        "validate": not skip_validation,
    }
    with spinner():
        _ = safe_request("recordings/spectrogram", "POST", json=json)
    raise typer.Exit()
