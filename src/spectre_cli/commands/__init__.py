# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Callable
from functools import wraps

import typer
from spectre_core.logging import PROCESS_TYPES

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
SUPPRESS_DOUBLECHECK_HELP = "Suppress doublecheck prompts on file operations"
PID_HELP = "Process ID"
FILE_NAME_HELP = "File name (specified without extension)"
AS_COMMAND_HELP = "Output is expressed as a runnable command"
INSTRUMENT_CODE_HELP = "The case-sensitive CALLISTO instrument code"
ABSOLUTE_TOLERANCE_HELP = "The value of the 'atol' keyword argument for np.isclose"
PER_SPECTRUM_HELP = "Show validated status per spectrum."

def secho_response(func: Callable):
    """Print the jsendified response from the spectre server"""
    @wraps(func)  # Preserves the original function's name and metadata
    def wrapper(*args, **kwargs):
        jsend_response = func(*args, **kwargs)
        if jsend_response['status'] == "success":
            typer.secho(jsend_response['data'])
        elif jsend_response['status'] == "error":
            typer.secho(jsend_response["message"], fg="yellow")
    return wrapper

