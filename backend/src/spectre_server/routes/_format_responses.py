# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing
import functools
import os
import traceback
import enum
import http

import flask

"""This module implements the JSend specification. For more information, please refer
to https://github.com/omniti-labs/jsend"""


class _JsendStatus(enum.Enum):
    """A defined `Jsend` status code.

    :ivar SUCCESS: The Jsend `success` status.
    :ivar FAIL: The Jsend `FAIL` status.
    :ivar ERROR: The Jsend `ERROR` status.
    """

    SUCCESS = "success"
    FAIL = "fail"
    ERROR = "error"


def _make_jsend_response(
    status: _JsendStatus,
    data: None | str | list[typing.Any] | dict[str, typing.Any] = None,
    message: typing.Optional[str] = None,
    code: typing.Optional[int] = None,
) -> flask.Response:
    """Create a JSend-compliant API response.

    :param status: The Jsend status.
    :param data: The value for the `data` key, as per the Jsend specification, defaults to None.
    Must be JSON serialisable (e.g., a string, a dictionary, or a structure compatible with JSON
    encoding). Defaults to None.
    :param message: The value for the `message` key, as per the Jsend specification, defaults to None.
    :code: The value of the `code` key, as per the Jsend specification, defaults to None.
    """
    jsend_dict: dict[str, typing.Any] = {"status": status.value}

    # Handle success status
    if status == _JsendStatus.SUCCESS or status == _JsendStatus.FAIL:
        # 'data' is a mandatory field for responses with 'fail' and 'success' statuses.
        if data is None:
            raise ValueError(
                f"The `data` key must have a value for `success` and `fail` "
                f"JSend status codes."
            )
        jsend_dict["data"] = data
        return flask.jsonify(jsend_dict)

    # Handle error status
    elif status == _JsendStatus.ERROR:
        if not message:
            raise ValueError("The 'message' field is required for 'error' responses.")
        jsend_dict["message"] = message

        # 'data' is an optional key for responses with status 'error'
        if data is not None:
            jsend_dict["data"] = data

        # 'code' is an optional key for responses with status 'error'
        if code is not None:
            jsend_dict["code"] = str(code)

        return flask.jsonify(jsend_dict)


P = typing.ParamSpec("P")
# Loosen type hinting to support any JSON-compatible data structures.
# Additionally, permit `Response` objects, under the assumption they are produced by `send_from_directory`.
T = typing.TypeVar("T", bound=None | str | list[typing.Any] | dict[str, typing.Any])


def jsendify_response(
    func: typing.Callable[P, T],
) -> typing.Callable[P, flask.Response]:
    """Wrap route calls for simplified responses.

    :func param: A callable with JSON serialisable return.
    :return: The input function wrapped such that it returns a `JSend` compliant response.
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> flask.Response:
        try:
            data = func(*args, **kwargs)
            return _make_jsend_response(
                _JsendStatus.SUCCESS, data=data, code=http.HTTPStatus.OK
            )
        except:  # simplistic treatment, any exceptions are interpreted as JSend errors.
            return _make_jsend_response(
                _JsendStatus.ERROR,
                message=(
                    f"An internal server error has occured. "
                    f"Received the following error: \n{traceback.format_exc()}"
                    f"Use `spectre get log` for more information."
                ),
                code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    return wrapper


def serve_from_directory(
    file_path: str,
) -> flask.Response:
    """Light wrapper for Flask's `send_from_directory`."""
    parent_dir, file_name = os.path.split(file_path)
    return flask.send_from_directory(parent_dir, file_name, as_attachment=True)
