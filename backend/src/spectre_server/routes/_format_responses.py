# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional, Callable, ParamSpec, TypeVar, Any
from functools import wraps
import os
import traceback
from enum import Enum

from flask import jsonify, Response, send_from_directory, current_app
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
    data: None|str|list[Any]|dict[str, Any] = None,
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
    jsend_dict: dict[str, None|str|list[Any]|dict[str, Any]] = {"status": status.value}

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
# Additionally, permit `Response` objects, under the assumption they are produced by `send_from_directory`.
T = TypeVar("T", bound=None|str|list[Any]|dict[str, Any]|Response)

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
            
            # Handle the case where the data returned is from Flask's `send_from_directory`.
            # Here, we want the response to propagate through unchanged if it succeeds, and
            # create a fails JSend compliant response if it fails. 
            # TODO: Do a stricter check on the `Response` object to ensure this is the case.
            if isinstance(data, Response):
                return data
            
            return make_jsend_response(JsendStatus.SUCCESS,
                                       data = data,
                                       code = HTTPStatus.OK)
        except: # simplistic treatment, any exceptions are interpreted as JSend errors.
            return make_jsend_response(JsendStatus.ERROR,
                                        message = (f"An internal server error has occured. "
                                                   f"Received the following error: \n{traceback.format_exc()}"
                                                   f"Use `spectre get log` for more information."),
                                        code = HTTPStatus.INTERNAL_SERVER_ERROR)
    return wrapper


def serve_from_directory(
    file_path: str,
) -> Response:
    """Light wrapper for Flask's `send_from_directory`."""
    parent_dir, file_name = os.path.split(file_path)
    return send_from_directory(parent_dir, file_name, as_attachment=True)
