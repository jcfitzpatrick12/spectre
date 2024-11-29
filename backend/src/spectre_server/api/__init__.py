# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional

from flask import jsonify
from http import HTTPStatus

ALLOWED_STATUSES = {"success", "fail", "error"}
DATA_REQUIRED_STATUSES = {"success", "fail"}
MESSAGE_REQUIRED_STATUSES = {"error"}


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