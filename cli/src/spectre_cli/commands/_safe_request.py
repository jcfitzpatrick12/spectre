# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import requests
import os
from typing import Callable, Any, ParamSpec
from functools import wraps
from typing import Optional

import typer

P = ParamSpec('P')
def _catch_response_errors(
    func: Callable[P, Any]
) -> Callable[P, dict[str, Any]]:
    """Standardise error handling on making a request, assuming a `Jsend` compliant response."""
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs):
        try:
            jsend_dict = func(*args, **kwargs)

        except requests.exceptions.ConnectionError:
            typer.secho(("Error: Unable to connect to the spectre-server. "
                         "Is the container running? "), fg="yellow")
            raise typer.Exit(1)
        
        status = jsend_dict["status"]

        # on success, return the response to be handled by the caller
        if status == "success":
            return jsend_dict
        
        # otherwise, we standardise error handling for non-success response statuses
        elif status == "error":
            typer.secho((f"{jsend_dict['message']}"), fg = "yellow")
            raise typer.Exit(1)
        
        elif status == "fail":
            typer.secho((f"Error: Bad client request. "
                         f"{jsend_dict['data']}"), fg = "yellow")
            raise typer.Exit(1)
        
        else:
            raise ValueError((f"Unexpected response status. "
                             f"Got {status}, expected one of 'success', 'error' or 'fail'"))
    return wrapper


@_catch_response_errors
def safe_request(
    route_url: str, 
    method: str,
    json: Optional[dict] = None,
    params: Optional[dict] = None
) -> dict:
    """Send a request to the specified URL and return the JSON response.

    Handles requests to the `spectre-server` running locally on the loopback IP (127.0.0.1:5000).

    :param route_url: Endpoint path to append to the base URL.
    :param method: HTTP method to use for the request (e.g., 'GET', 'POST').
    :param json: Optional JSON payload for the request body.
    :param params: Optional query parameters for the request.
    :return: Parsed JSON response as a dictionary.
    """

    if route_url.startswith("/"):
        route_url.lstrip("/")
        
    # Use the base URL of the spectre-server running on the spectre-network
    full_url = os.path.join("http://spectre-server:5000", route_url)

    response = requests.request(method,
                                full_url,
                                json = json,
                                params = params)
    response.raise_for_status()
    return response.json()