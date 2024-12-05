# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import requests
import os
from typing import Callable
from functools import wraps
from typing import Optional

import typer

from spectre_core.logging import PROCESS_TYPES

# Base URL of the locally running spectre-server, specifying the loopback IP and port 5000
BASE_URL = f"http://127.0.0.1:5000"

RECEIVER_NAME_HELP = "The name of the receiver"
MODE_HELP = "The operating mode for the receiver"
TAG_HELP = "The capture config tag"
SECONDS_HELP = "Seconds component of the session duration"
MINUTES_HELP = "Minutes component of the session duration"
HOURS_HELP = "Hours component of the session duration"
DAY_HELP = "Day of the month (numeric)"
MONTH_HELP = "Month of the year (numeric)"
YEAR_HELP = "Year (numeric)"
FORCE_RESTART_HELP = "If a worker process stops unexpectedly, terminate all subprocesses and restart the capture session"
FORCE_UPDATE_HELP = "Force configuration files update if chunks exist under the given tag"
PARAMS_HELP = "Pass arbitrary key-value pairs"
PROCESS_TYPE_HELP = f"Processes may be one of {PROCESS_TYPES}"
EXTENSIONS_HELP = "File extensions"
FORCE_HELP = "Suppress warnings on file operations"
PID_HELP = "Process ID"
FILE_NAME_HELP = "File name (specified without extension)"
AS_COMMAND_HELP = "Output is expressed as a runnable command"
INSTRUMENT_CODE_HELP = "The case-sensitive CALLISTO instrument code"
ABSOLUTE_TOLERANCE_HELP = "The value of the 'atol' keyword argument for np.isclose"
PER_SPECTRUM_HELP = "Show validated status per spectrum."


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
                 payload: Optional[dict] = None
) -> dict:
    """Request a response at the input route URL.
    
    Safety is enforce by the accompanying decorator.
    """

    if route_url.startswith("/"):
        route_url.lstrip("/")
    
    full_url = os.path.join(BASE_URL, route_url)

    response = requests.request(method,
                                full_url,
                                json = payload)
    return response.json()


