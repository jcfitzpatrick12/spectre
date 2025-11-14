# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""Functions which are shared among the CLI commands."""

# TODO: Refactor later, when it makes sense to do so.

import typing
import requests
import os
import contextlib

import typer
import yaspin

from ..config import SPECTRE_SERVER


@contextlib.contextmanager
def spinner():
    with yaspin.yaspin(text="In progress... "):
        yield


def confirm_with_user() -> None:
    """Prompt the user to confirm an action."""
    confirmed = typer.confirm("Are you sure you want to do this?")
    if not confirmed:
        raise typer.Exit(1)


def safe_request(
    route_url: str,
    method: str,
    json: typing.Optional[dict] = None,
    params: typing.Optional[dict] = None,
    require_confirmation: bool = False,
    non_interactive: bool = False,
) -> dict:
    """Send a request to the `spectre-server` and handle jsend-style responses.

    :param route_url: Endpoint path to append to the `spectre-server` base URL. This base URL is defined by the environment variables `SPECTRE_SERVER_HOST`, `SPECTRE_SERVER_PORT` or `SPECTRE_SERVER`.
    :param method: HTTP method to use for the request (e.g., 'GET', 'POST').
    :param json: typer.Optional JSON payload for the request body.
    :param params: typer.Optional query parameters for the request.
    :param require_confirmation: If True, prompt the user if they'd like to continue.
    :param suppress_confirmation: If True, ignore the `require_confirmation` flag, and continue with the request.
    :return: Parsed JSON response as a dictionary.
    """
    if require_confirmation and not non_interactive:
        confirm_with_user()

    if route_url.startswith("/"):
        route_url = route_url.lstrip("/")

    full_url = os.path.join(SPECTRE_SERVER, route_url)

    try:
        response = requests.request(method, full_url, json=json, params=params)
        response.raise_for_status()
        jsend_dict = response.json()
    except requests.exceptions.ConnectionError:
        typer.secho(
            "Error: Unable to connect to the spectre-server. Is the container running?",
            fg="yellow",
        )
        raise typer.Exit(1)

    status = jsend_dict.get("status")

    if status == "success":
        return jsend_dict

    elif status == "error":
        typer.secho(jsend_dict.get("message", "An error occurred."), fg="yellow")
        raise typer.Exit(1)

    elif status == "fail":
        typer.secho(f"Error: Bad client request. {jsend_dict.get('data')}", fg="yellow")
        raise typer.Exit(1)

    else:
        raise ValueError(
            f"Unexpected response status. Got {status}, expected one of 'success', 'error' or 'fail'."
        )


def get_config_file_name(
    file_name: typing.Optional[str], tag: typing.Optional[str]
) -> str:
    """Given either a file name, or the tag, build the config file name.

    Primarily used for input validation, where the user can specify either or via the CLI.
    """
    if not (file_name is None) ^ (tag is None):
        raise ValueError("Specify exactly one of the tag or file name.")
    return file_name or f"{tag}.json"
