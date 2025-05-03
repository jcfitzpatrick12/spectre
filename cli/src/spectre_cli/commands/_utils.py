# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""Functions which are shared among the CLI commands.
"""

# TODO: Refactor later, when it makes sense to do so.

import requests
import os
import typer
from typing import Optional
from datetime import date, datetime, timezone

from ..config import SPECTRE_SERVER


def confirm_with_user(
) -> None:
    """Prompt the user to confirm an action."""
    confirmed = typer.confirm("Are you sure you want to do this?")
    if not confirmed:
        raise typer.Exit("Aborted by user.")
        

def safe_request(
    route_url: str, 
    method: str,
    json: Optional[dict] = None,
    params: Optional[dict] = None,
    require_confirmation: bool = False,
    suppress_confirmation: bool = False
) -> dict:
    """Send a request to the `spectre-server` and handle jsend-style responses.

    :param route_url: Endpoint path to append to the `spectre-server` base URL. This base URL is defined by the environment variables `SPECTRE_SERVICE_HOST`, `SPECTRE_SERVICE_PORT` or `SPECTRE_SERVER`.
    :param method: HTTP method to use for the request (e.g., 'GET', 'POST').
    :param json: Optional JSON payload for the request body.
    :param params: Optional query parameters for the request.
    :param require_confirmation: If True, prompt the user if they'd like to continue.
    :param suppress_confirmation: If True, ignore the `require_confirmation` flag, and continue with the request.
    :return: Parsed JSON response as a dictionary.
    """
    if require_confirmation and not suppress_confirmation:
        confirm_with_user()
        
    if route_url.startswith("/"):
        route_url = route_url.lstrip("/")

    full_url = os.path.join(SPECTRE_SERVER, route_url)

    try:
        response = requests.request(method, full_url, json=json, params=params)
        response.raise_for_status()
        jsend_dict = response.json()
    except requests.exceptions.ConnectionError:
        typer.secho("Error: Unable to connect to the spectre-server. Is the container running?", fg="yellow")
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
        raise ValueError(f"Unexpected response status. Got {status}, expected one of 'success', 'error' or 'fail'.")
    

def build_date_path(
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> str:
    """
    Construct a URL date path in one of the allowed formats:
    
    - "YYYY"
    - "YYYY/MM"
    - "YYYY/MM/DD"

    If no parts are provided, returns an empty string.
    """
    today = datetime.now(timezone.utc).date()

    if day is not None and month is None:
        raise ValueError("Day cannot be specified without month.")
    if month is not None and year is None:
        raise ValueError("Month cannot be specified without year.")

    # If no date parts are provided, return empty path
    if year is None:
        return ""

    # Use minimal defaults to validate
    d = day if day is not None else 1
    m = month if month is not None else 1

    try:
        constructed = date(year, m, d)
    except ValueError as e:
        raise ValueError(f"Invalid date: {e}")

    if constructed > today:
        raise ValueError("Date cannot be in the future.")

    # Build path
    if day is not None:
        return f"{year}/{month:02d}/{day:02d}"
    elif month is not None:
        return f"{year}/{month:02d}"
    else:
        return f"{year}"
    
    
def get_capture_config_file_name(
    file_name: Optional[str],
    tag: Optional[str]
) -> None:
    """Given either a file name, or the tag, build the capture config file name.
    
    Primarily used for input validation, where the user can specify either or via the CLI.
    """
    if not (file_name is None) ^ (tag is None):
        raise ValueError("Specify either the tag or file name, not both.")
    return file_name or f"{tag}.json"
