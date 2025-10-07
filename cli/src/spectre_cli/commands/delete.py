# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typer import Typer, Option, Exit

from ._utils import safe_request, get_config_file_name
from ._secho_resources import (
    secho_stale_resource,
    secho_stale_resources,
    secho_existing_resource,
    secho_existing_resources,
)


delete_typer = Typer(help="Delete resources.")


@delete_typer.command(help="Delete logs.")
def logs(
    process_types: list[str] = Option(
        [],
        "--process-type",
        help="Delete all logs with this process type, specifying one of 'worker' or 'user'. If not provided, nothing will be deleted.",
    ),
    year: int = Option(None, "--year", "-y", help="Only delete logs under this year."),
    month: int = Option(
        None, "--month", "-m", help="Only delete logs under this month."
    ),
    day: int = Option(None, "--day", "-d", help="Only delete logs under this day."),
    non_interactive: bool = Option(
        False, "--non-interactive", help="Suppress any interactive prompts."
    ),
    dry_run: bool = Option(
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
        "year": year,
        "month": month,
        "day": day,
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
    raise Exit()


@delete_typer.command(help="Delete batch files.", deprecated=True)
def batch_files(
    tags: list[str] = Option(
        [],
        "--tag",
        "-t",
        help="Delete all batch files with this tag. If not provided, nothing will be deleted.",
    ),
    extensions: list[str] = Option(
        [],
        "--extension",
        "-e",
        help="Delete all batch files with this file extension. If not provided, nothing will be deleted.",
    ),
    year: int = Option(
        None, "--year", "-y", help="Only delete batch files under this year."
    ),
    month: int = Option(
        None, "--month", "-m", help="Only delete batch files under this month."
    ),
    day: int = Option(
        None, "--day", "-d", help="Only delete batch files under this day."
    ),
    non_interactive: bool = Option(
        False, "--non-interactive", help="Suppress any interactive prompts."
    ),
    dry_run: bool = Option(
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
    raise Exit()


@delete_typer.command(help="Delete files.")
def files(
    tags: list[str] = Option(
        [],
        "--tag",
        "-t",
        help="Delete all files with this tag. If not provided, nothing will be deleted.",
    ),
    extensions: list[str] = Option(
        [],
        "--extension",
        "-e",
        help="Delete all files with this file extension. If not provided, nothing will be deleted.",
    ),
    year: int = Option(None, "--year", "-y", help="Only delete files under this year."),
    month: int = Option(
        None, "--month", "-m", help="Only delete files under this month."
    ),
    day: int = Option(None, "--day", "-d", help="Only delete files under this day."),
    non_interactive: bool = Option(
        False, "--non-interactive", help="Suppress any interactive prompts."
    ),
    dry_run: bool = Option(
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
    raise Exit()


@delete_typer.command(help="Delete a capture config.", deprecated=True)
def capture_config(
    tag: str = Option(None, "--tag", "-t", help="The unique identifier."),
    file_name: str = Option(None, "-f", help="The file name.", metavar="<tag>.json"),
    non_interactive: bool = Option(
        False, "--non-interactive", help="Suppress any interactive prompts."
    ),
    dry_run: bool = Option(
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
    raise Exit()


@delete_typer.command(help="Delete a config.")
def config(
    tag: str = Option(None, "--tag", "-t", help="The unique identifier."),
    file_name: str = Option(None, "-f", help="The file name.", metavar="<tag>.json"),
    non_interactive: bool = Option(
        False, "--non-interactive", help="Suppress any interactive prompts."
    ),
    dry_run: bool = Option(
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
    raise Exit()
