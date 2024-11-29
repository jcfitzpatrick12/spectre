# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional, Callable

import logging

from flask import jsonify, request
from http import HTTPStatus

from spectre_core.logging import configure_root_logger

ALLOWED_STATUSES = {"success", "fail", "error"}
DATA_REQUIRED_STATUSES = {"success", "fail"}
MESSAGE_REQUIRED_STATUSES = {"error"}
DEFAULT_LOG_LEVEL = logging.info

def jsend_response(
    status: str,
    data: Optional[dict] = None,
    message: Optional[str] = None,
    code: Optional[HTTPStatus] = None):
    """All API responses adhere to https://github.com/omniti-labs/jsend"""
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid status. Expected one of {ALLOWED_STATUSES}, got '{status}'.")

    if status in MESSAGE_REQUIRED_STATUSES and message is None:
        raise ValueError(f"Message is required for status '{status}', but got None.")

    response = {"status": status}

    if status in DATA_REQUIRED_STATUSES:
        # if data is required, even if it is missing, set to null
        response["data"] = data

    if status == "error":
        response["message"] = message
        if code is not None:
            response["code"] = code
        if data is not None:
            response["data"] = data 

    return jsonify(response)


def configure_logging(func: Callable):
    def wrapper(*args, **kwargs):
        data = request.get_json()
        data.get("log_level")
        configure_root_logger("USER", data.get("log_level", 10))
        return func(*args, **kwargs)
    return wrapper
