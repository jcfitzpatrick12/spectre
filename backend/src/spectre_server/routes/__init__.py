# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional, Callable
from functools import wraps
import os
import traceback

from flask import jsonify, Response
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

    jsend_dict = {"status": status}

    # Handle success status
    if status == "success" or status == "fail":
        # 'data' is a mandatory field for responses with 'fail' and 'success' statuses.
        # if None, the value must be null.
        jsend_dict["data"] = data
        return jsonify(jsend_dict)


    # Handle error status
    elif status == "error":
        if not message:
            raise ValueError("The 'message' field is required for 'error' responses.")
        jsend_dict["message"] = message

        # 'data' is an optional key for responses with status 'error'
        if data is not None:
            jsend_dict["data"] = data

        # 'code' is an optional key for responses with status 'error'
        if code is not None:
            jsend_dict["code"] = code

        return jsonify(jsend_dict)


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
                                                    f"Please use 'spectre get log --pid {user_pid}` for more details"),
                                        code = HTTPStatus.INTERNAL_SERVER_ERROR)
    return wrapper