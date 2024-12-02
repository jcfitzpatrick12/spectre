# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Callable
from functools import wraps

import typer

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