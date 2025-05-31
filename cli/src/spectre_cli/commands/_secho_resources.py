# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""Print resource endpoints to `stdout`."""

import typer
import yaml


def pprint_dict(d: dict) -> None:
    """Pretty print a dictionary in the yaml format."""
    print(yaml.dump(d, sort_keys=True, default_flow_style=False))


def secho_new_resource(endpoint: str) -> None:
    """Print the URL of a newly created resource."""
    typer.secho(endpoint, fg="green")


def secho_new_resources(endpoints: list[str]) -> None:
    """Print the URLs of newly created resources."""
    for endpoint in endpoints:
        secho_new_resource(endpoint)


def secho_existing_resource(endpoint: str) -> None:
    """Print the URL of an existing resource."""
    typer.secho(endpoint)


def secho_existing_resources(endpoints: list[str]) -> None:
    """Print the URLs of existing resources."""
    for endpoint in endpoints:
        secho_existing_resource(endpoint)


def secho_stale_resource(endpoint: str) -> None:
    """Print the URL of a resource which no longer exists."""
    typer.secho(endpoint, fg="yellow")


def secho_stale_resources(endpoints: list[str]) -> None:
    """Print the URLs of resources which no longer exist."""
    for endpoint in endpoints:
        secho_stale_resource(endpoint)
