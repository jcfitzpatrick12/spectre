# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import time

import requests
import typer

from ..config import SPECTRE_SERVER
from ._secho_resources import secho_new_resources
from ._utils import safe_request, spinner

record_typer = typer.Typer(help="Start recording data.")

_DEFAULT_MAX_RESTARTS = 5
_DEFAULT_FORCE_RESTART = False
_DEFAULT_SKIP_VALIDATION = False
_TERMINAL_STATES = frozenset({"completed", "stopped", "failed"})
_POLL_INTERVAL_SECONDS = 0.2


def _url_id(url: str) -> str:
    return url.rsplit("/", 1)[-1]


def _request_stop(id: str) -> None:
    """Best-effort stop request. Swallow errors so cleanup covers every id."""
    try:
        requests.patch(
            f"{SPECTRE_SERVER}/recordings/{id}",
            json={"state": "stopped"},
            timeout=5,
        )
    except requests.RequestException:
        pass


def _wait_terminal(ids: list[str]) -> dict[str, str]:
    """Block until every id reaches a terminal state; return {id: state}."""
    final: dict[str, str] = {}
    remaining = list(ids)
    while remaining:
        still_pending: list[str] = []
        for id in remaining:
            jsend_dict = safe_request(f"recordings/{id}", "GET")
            state = jsend_dict["data"]["state"]
            if state in _TERMINAL_STATES:
                final[id] = state
            else:
                still_pending.append(id)
        remaining = still_pending
        if remaining:
            time.sleep(_POLL_INTERVAL_SECONDS)
    return final


def _run_recording(
    kind: str,
    tags: list[str],
    duration: float,
    force_restart: bool,
    max_restarts: int,
    validate: bool,
    detach: bool,
) -> None:
    json = {
        "kind": kind,
        "tags": tags,
        "duration": duration,
        "force_restart": force_restart,
        "max_restarts": max_restarts,
        "validate": validate,
    }
    jsend_dict = safe_request("recordings", "POST", json=json)
    endpoints: list[str] = jsend_dict["data"]

    if detach:
        secho_new_resources(endpoints)
        raise typer.Exit()

    ids = [_url_id(u) for u in endpoints]
    try:
        with spinner():
            final = _wait_terminal(ids)
    except KeyboardInterrupt:
        typer.secho("\nInterrupted; requesting stop...", fg="yellow")
        for id in ids:
            _request_stop(id)
        with spinner():
            final = _wait_terminal(ids)
        for id in ids:
            typer.secho(f"{id}: {final.get(id, 'unknown')}", fg="yellow")
        raise typer.Exit(1)

    non_completed = [
        (id, state) for id, state in final.items() if state != "completed"
    ]
    if non_completed:
        for id, state in non_completed:
            typer.secho(f"{id}: {state}", fg="yellow")
        raise typer.Exit(1)
    raise typer.Exit()


@record_typer.command(help="Capture data from an SDR in real time.")
def signal(
    tags: list[str] = typer.Option(..., "--tag", "-t", help="The config tag."),
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
        help="If specified, do not validate config parameters.",
    ),
    detach: bool = typer.Option(
        False,
        "--detach",
        help="If specified, return immediately and let the recording run in the background.",
    ),
) -> None:
    _run_recording(
        kind="signal",
        tags=tags,
        duration=duration,
        force_restart=force_restart,
        max_restarts=max_restarts,
        validate=not skip_validation,
        detach=detach,
    )


@record_typer.command(
    help="Capture data from an SDR and post-process it into spectrograms in real time."
)
def spectrograms(
    tags: list[str] = typer.Option(..., "--tag", "-t", help="The config tag."),
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
        help="If specified, do not validate config parameters.",
    ),
    detach: bool = typer.Option(
        False,
        "--detach",
        help="If specified, return immediately and let the recording run in the background.",
    ),
) -> None:
    _run_recording(
        kind="spectrogram",
        tags=tags,
        duration=duration,
        force_restart=force_restart,
        max_restarts=max_restarts,
        validate=not skip_validation,
        detach=detach,
    )
