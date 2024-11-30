# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional
import os

from flask import jsonify
from http import HTTPStatus

ALLOWED_STATUSES = {"success", "fail", "error"}

def jsend_response(
    status: str, 
    data: Optional[dict] = None,
    message: Optional[str] = None,
    code: Optional[HTTPStatus] = None):
    """Create a standardised Jsend API response.
    
    Adheres to https://github.com/omniti-labs/jsend"""
    # avoid mutable default
    if data is None:
        data = {}

    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid status. Expected one of {ALLOWED_STATUSES}, but got: {status}")

    response = {"status": status}

    if status in ["fail", "success"]:
        # add the current pid (so user can find corresponding logs)
        data["pid"] = os.getpid()
        response["data"] = data
        return jsonify(response)

    elif status == "error":
        if message is None:
            raise ValueError(f"Message is required for status {status}, but got: {message}")
        response["message"] = message

        if data:
            response["data"] = data 
        if code is not None:
            response["code"] = code

        return jsonify(response)
    
    else:
        raise ValueError(f"Invalid status. Expected one of {ALLOWED_STATUSES}, but got: {status}")
