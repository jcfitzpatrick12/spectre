# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional, Callable, ParamSpec, TypeVar, Any
from functools import wraps
import os
import traceback
from enum import Enum

from flask import jsonify, Response
from http import HTTPStatus

"""This module implements the JSend specification. For more information, please refer
to https://github.com/omniti-labs/jsend"""

class JsendStatus(Enum):
    """A defined `Jsend` status code.
    
    :ivar SUCCESS: The Jsend `success` status.
    :ivar FAIL: The Jsend `FAIL` status.
    :ivar ERROR: The Jsend `ERROR` status.
    """
    SUCCESS = "success"
    FAIL    = "fail"
    ERROR   = "error"


def make_jsend_response(
    status: JsendStatus,
    data: Optional[str|dict[str, object]] = None,
    message: Optional[str] = None,
    code: Optional[int] = None
) -> Response:
    """Create a JSend-compliant API response.
    
    :param status: The Jsend status.
    :param data: The value for the `data` key, as per the Jsend specification, defaults to None.
    Must be JSON serialisable (e.g., a string, a dictionary, or a structure compatible with JSON 
    encoding). Defaults to None.
    :param message: The value for the `message` key, as per the Jsend specification, defaults to None.
    :code: The value of the `code` key, as per the Jsend specification, defaults to None.
    """
    jsend_dict: dict[str, str|dict[str, object]] = {"status": status.value}

    # Handle success status
    if status == JsendStatus.SUCCESS or status == JsendStatus.FAIL:
        # 'data' is a mandatory field for responses with 'fail' and 'success' statuses.
        if data is None:
            raise ValueError(f"The `data` key must have a value for `success` and `fail` "
                             f"JSend status codes.")
        jsend_dict["data"] = data
        return jsonify(jsend_dict)


    # Handle error status
    elif status == JsendStatus.ERROR:
        if not message:
            raise ValueError("The 'message' field is required for 'error' responses.")
        jsend_dict["message"] = message

        # 'data' is an optional key for responses with status 'error'
        if data is not None:
            jsend_dict["data"] = data

        # 'code' is an optional key for responses with status 'error'
        if code is not None:
            jsend_dict["code"] = str(code)

        return jsonify(jsend_dict)


P = ParamSpec("P")
# Loosen type hinting to support any JSON-compatible data structures.
T = TypeVar("T", bound=None|str|list[Any]|dict[str, Any])

def jsendify_response(
    func: Callable[P, T]
) -> Callable[P, Response]:
    """Wrap route calls for simplified responses.
    
    :func param: A callable with JSON serialisable return.
    :return: The input function wrapped such that it returns a `JSend` compliant response.
    """
    @wraps(func)  # Preserves the original function's name and metadata
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Response:
        try:
            data = func(*args, **kwargs)
            return make_jsend_response(JsendStatus.SUCCESS,
                                       data = data,
                                       code = HTTPStatus.OK)
        except: # simplistic treatment, any exceptions are interpreted as JSend errors.
            user_pid = os.getpid()
            return make_jsend_response(JsendStatus.ERROR,
                                        message = (f"An internal server error has occured. "
                                                   f"Received the following error: \n{traceback.format_exc()}"
                                                   f"Please use 'spectre get log --pid {user_pid}` for more details"),
                                        code = HTTPStatus.INTERNAL_SERVER_ERROR)
    return wrapper