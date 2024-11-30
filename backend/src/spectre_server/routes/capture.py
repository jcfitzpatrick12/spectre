# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from http import HTTPStatus
from typing import Optional

from flask import Blueprint, request
from flask.wrappers import Request

from spectre_server.routes import jsend_response
from spectre_server.services import capture

capture_blueprint = Blueprint("capture", __name__)

def _validate_capture_data(
        tag: Optional[str],
        seconds: Optional[int],
        hours: Optional[int],
        minutes: Optional[int],
        force_restart: Optional[b]

) -> Optional[Request]:
    # Validate types and constraints
    if not isinstance(tag, str) or not tag.strip():
        return jsend_response("fail", 
                              message = "'tag' must be a non-empty string",
                              code = HTTPStatus.BAD_REQUEST)
    if seconds is not None and (not isinstance(seconds, int)):
        return jsend_response("fail",
                              message = "'seconds' must be a non-negative integer",
                              code = HTTPStatus.BAD_REQUEST)
    if seconds is not None and (not isinstance(seconds, int)):
        return jsend_response("fail",
                              message = "'minutes' must be a non-negative integer",
                              code = HTTPStatus.BAD_REQUEST)
    if seconds is not None and (not isinstance(seconds, int)):
        return jsend_response("fail",
                              message = "'hours' must be a non-negative integer",
                              code = HTTPStatus.BAD_REQUEST)
    if force_restart is not None and not isinstance(force_restart, bool):
        return jsend_response("fail",
                              message = "'hours' must be a non-negative integer",
                              code = HTTPStatus.BAD_REQUEST)
    return None

@capture_blueprint.route("/start", methods=["POST"])
def start():

    data = request.get_json()
    tag = data.get("tag")
    seconds = data.get("seconds")
    minutes = data.get("minutes")
    hours = data.get("hours")
    force_restart = data.get("force_restart")


    validation_errors = _validate_capture_data(tag,
                                               seconds,
                                               hours,
                                               minutes,
                                               force_restart)
    if validation_errors:
        return validation_errors
    
    capture.start(tag,
                  seconds,
                  minutes,
                  hours,
                  force_restart)

    return jsend_response("success",
                          message = "Capture completed successfully",
                          code = HTTPStatus.OK)
