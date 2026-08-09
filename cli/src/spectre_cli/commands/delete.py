# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer

from ._utils import (
    safe_request,
    get_config_file_name,
    confirm_with_user,
    RecordingState,
    ProcessType,
)
from ._secho_resources import (
    secho_stale_resource,
    secho_stale_resources,
    secho_existing_resource,
    secho_existing_resources,
)

delete_typer = typer.Typer(help="Delete resources.")


@delete_typer.command(help="Delete logs.")
def logs(
    process_types: list[ProcessType] = typer.Option(
        [],
        "--process-type",
        help="Delete all logs with this process type. If not provided, nothing will be deleted.",
    ),
    non_interactive: bool = typer.Option(
        False, "--non-interactive", help="Suppress any interactive prompts."
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Display which files would be deleted without actually deleting them.",
    ),
) -> None:
    if dry_run:
        non_interactive = True

    params = {
        "process_type": process_types,
        "dry_run": dry_run,
    }

    jsend_dict = safe_request(
        f"spectre-data/logs",
        "DELETE",
        params=params,
        require_confirmation=True,
        non_interactive=non_interactive,
    )
    endpoints = jsend_dict["data"]
    if not dry_run:
        secho_stale_resources(endpoints)
    else:
        secho_existing_resources(endpoints)
    raise typer.Exit()


@delete_typer.command(help="Delete files.")
def files(
    tags: list[str] = typer.Option(
        [],
        "--tag",
        "-t",
        help="Delete all files with this tag. If not provided, nothing will be deleted.",
    ),
    extensions: list[str] = typer.Option(
        [],
        "--extension",
        "-e",
        help="Delete all files with this file extension. If not provided, nothing will be deleted.",
    ),
    year: int = typer.Option(
        None, "--year", "-y", help="Only delete files under this year."
    ),
    month: int = typer.Option(
        None, "--month", "-m", help="Only delete files under this month."
    ),
    day: int = typer.Option(
        None, "--day", "-d", help="Only delete files under this day."
    ),
    non_interactive: bool = typer.Option(
        False, "--non-interactive", help="Suppress any interactive prompts."
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Display which files would be deleted without actually deleting them.",
    ),
) -> None:
    if dry_run:
        non_interactive = True
    params = {
        "extension": extensions,
        "tag": tags,
        "dry_run": dry_run,
        "year": year,
        "month": month,
        "day": day,
    }
    jsend_dict = safe_request(
        f"spectre-data/batches",
        "DELETE",
        params=params,
        require_confirmation=True,
        non_interactive=non_interactive,
    )
    endpoints = jsend_dict["data"]
    if not dry_run:
        secho_stale_resources(endpoints)
    else:
        secho_existing_resources(endpoints)
    raise typer.Exit()


@delete_typer.command(help="Delete a config.")
def config(
    tag: str = typer.Option(None, "--tag", "-t", help="The unique identifier."),
    file_name: str = typer.Option(
        None, "-f", help="The file name.", metavar="<tag>.json"
    ),
    non_interactive: bool = typer.Option(
        False, "--non-interactive", help="Suppress any interactive prompts."
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Display which files would be deleted without actually deleting them.",
    ),
) -> None:
    if dry_run:
        non_interactive = True
    file_name = get_config_file_name(file_name, tag)
    params = {"dry_run": dry_run}
    jsend_dict = safe_request(
        f"spectre-data/configs/{file_name}",
        "DELETE",
        params=params,
        require_confirmation=True,
        non_interactive=non_interactive,
    )
    endpoint = jsend_dict["data"]
    if not dry_run:
        secho_stale_resource(endpoint)
    else:
        secho_existing_resource(endpoint)
    raise typer.Exit()


@delete_typer.command(help="Delete a recording.")
def recording(
    recording_id: str = typer.Option(
        ..., "--recording-id", help="The unique identifier of the recording."
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        help="Suppress any interactive prompts.",
    ),
) -> None:
    jsend_dict = safe_request(
        f"recordings/{recording_id}",
        "DELETE",
        require_confirmation=True,
        non_interactive=non_interactive,
    )
    endpoint = jsend_dict["data"]
    secho_stale_resource(endpoint)
    raise typer.Exit()


@delete_typer.command(help="Delete recordings.")
def recordings(
    states: list[RecordingState] = typer.Option(
        [],
        "--state",
        help="Delete all recordings with this state. If not provided, nothing will be deleted.",
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        help="Suppress any interactive prompts.",
    ),
) -> None:
    endpoints: list[str] = []
    for state in states:
        jsend_dict = safe_request("recordings", "GET", params={"state": state})
        endpoints.extend(jsend_dict["data"])

    if not non_interactive:
        confirm_with_user()

    for endpoint in endpoints:
        recording_id = endpoint.split("/")[-1]
        result = safe_request(f"recordings/{recording_id}", "DELETE")
        secho_stale_resource(result["data"])

    raise typer.Exit()
