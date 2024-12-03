# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import Response
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
    code: Optional[int] = None
) -> Response:
    """Create a JSEND-compliant API response.

    Please refer to: https://github.com/omniti-labs/jsend
    """

    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid status: '{status}'. Must be one of {ALLOWED_STATUSES}.")

    response = {"status": status}

    # Handle success status
    if status == "success" or status == "fail":
        # 'data' is a mandatory field for responses with 'fail' and 'success' statuses.
        # if None, the value must be null.
        response["data"] = data
        return jsonify(response)


    # Handle error status
    elif status == "error":
        if not message:
            raise ValueError("The 'message' field is required for 'error' responses.")
        response["message"] = message

        # 'data' is an optional key for responses with status 'error'
        if data is not None:
            response["data"] = data

        # 'code' is an optional key for responses with status 'error'
        if code is not None:
            response["code"] = code

        return jsonify(response)

def jsendify_response(func: Callable):
    """Wrap route calls for simplified responses.
    
    Returns `jsend` formatted responses.
    """
    @wraps(func)  # Preserves the original function's name and metadata
    def wrapper(*args, **kwargs):
        try:
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