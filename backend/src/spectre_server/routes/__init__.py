# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import Optional, Callable
from functools import wraps
import os
import traceback

from flask import jsonify
from http import HTTPStatus

ALLOWED_STATUSES = {"success", "fail", "error"}

def make_jsend_response(
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


def jsendify_response(func: Callable):
    """Wrap route calls for simplified responses.
    
    Returns `jsend` formatted responses.
    """
    @wraps(func)  # Preserves the original function's name and metadata
    def wrapper(*args, **kwargs):
        try:
            # _LOGGER.info()
            data = func(*args, **kwargs)
            return make_jsend_response("success",
                                        data = data,
                                        code = HTTPStatus.OK)
        except:
            user_pid = os.getpid()
            return make_jsend_response("error",
                                        message = (f"An internal server error has occured. "
                                                    f"Received the following error: \n{traceback.format_exc()}"
                                                    f"Please use 'spectre print log --pid {user_pid}` for more details"),
                                        code = HTTPStatus.INTERNAL_SERVER_ERROR)
    return wrapper