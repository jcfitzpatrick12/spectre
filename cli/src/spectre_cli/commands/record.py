# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import time

import typer

from ._utils import safe_request, safe_request_from_endpoint, spinner
from ._secho_resources import secho_new_resource

record_typer = typer.Typer(help="Start recording data.")

_DEFAULT_MAX_RESTARTS = 5
_DEFAULT_FORCE_RESTART = False
_DEFAULT_SKIP_VALIDATION = False


def _record(
    tag: str,
    kind: str,
    duration: float,
    force_restart: bool,
    max_restarts: int,
    skip_validation: bool,
    detach: bool,
) -> None:
    jsend_dict = safe_request(
        "recordings",
        "POST",
        json={
            "tag": tag,
            "kind": kind,
            "duration": duration,
            "force_restart": force_restart,
            "max_restarts": max_restarts,
            "validate": not skip_validation,
        },
    )
    endpoint = jsend_dict["data"]
    secho_new_resource(endpoint)

    if detach:
        raise typer.Exit()

    try:
        with spinner():
            while True:
                jsend_dict = safe_request_from_endpoint(endpoint, "GET")
                state = jsend_dict["data"]["state"]
                if state != "running":
                    break
                time.sleep(1)
    except KeyboardInterrupt:
        safe_request_from_endpoint(endpoint, "PATCH", json={"stop_requested": True})
        typer.secho("stopped", fg="yellow")
        raise typer.Exit()

    if state == "failed":
        typer.secho("failed", fg="yellow")
        raise typer.Exit(1)

    raise typer.Exit()


@record_typer.command(help="Capture data from an SDR in real time.")
def signal(
    tag: str = typer.Option(
        ..., "--tag", "-t", help="The unique identifier of the config."
    ),
    duration: float = typer.Option(
        ...,
        "--duration",
        "-d",
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
        help="If specified, do not validate the parameters.",
    ),
    detach: bool = typer.Option(
        False,
        "--detach",
        "-D",
        help="If specified, return immediately and leave the recording running in the background.",
    ),
) -> None:
    _record(
        tag, "signal", duration, force_restart, max_restarts, skip_validation, detach
    )


@record_typer.command(
    help="Capture data from an SDR and post-process it into spectrograms in real time."
)
def spectrograms(
    tag: str = typer.Option(
        ..., "--tag", "-t", help="The unique identifier of the config."
    ),
    duration: float = typer.Option(
        ...,
        "--duration",
        "-d",
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
        help="If specified, do not validate the parameters.",
    ),
    detach: bool = typer.Option(
        False,
        "--detach",
        "-D",
        help="If specified, return immediately and leave the recording running in the background.",
    ),
) -> None:
    _record(
        tag,
        "spectrogram",
        duration,
        force_restart,
        max_restarts,
        skip_validation,
        detach,
    )
