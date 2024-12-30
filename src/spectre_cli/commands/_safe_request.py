# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import requests
import os
from typing import Callable
from functools import wraps
from typing import Optional

import typer

# Base URL of the locally running spectre-server, specifying the loopback IP and port 5000
_BASE_URL = f"http://127.0.0.1:5000"

def _catch_response_errors(func: Callable):
    """Standardised error handling on making a request.
    
    Assumes jsend formatted responses.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            jsend_dict = func(*args, **kwargs)

        except requests.exceptions.ConnectionError:
            typer.secho(("Error: Unable to connect to the spectre-server. "
                         "Is the container running? "
                         "You can check with 'docker container list' "), fg="yellow")
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
def safe_request(route_url: str, 
                 method: str,
                 json: Optional[dict] = None,
                 params: Optional[dict] = None
) -> dict:
    """Request a response at the input route URL.
    
    Safety is enforce by the accompanying decorator.
    """

    if route_url.startswith("/"):
        route_url.lstrip("/")
    
    full_url = os.path.join(_BASE_URL, route_url)

    response = requests.request(method,
                                full_url,
                                json = json,
                                params = params)
    response.raise_for_status()
    return response.json()