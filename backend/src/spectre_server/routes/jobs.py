# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import Blueprint, request

from ..services import jobs
from ._format_responses import jsendify_response


jobs_blueprint = Blueprint("jobs", __name__, url_prefix="/jobs")


@jobs_blueprint.route("/capture", methods=["POST"])
@jsendify_response
def capture() -> str:
    json = request.get_json()
    tag = json.get("tag")
    seconds = json.get("seconds")
    minutes = json.get("minutes")
    hours = json.get("hours")
    force_restart = json.get("force_restart")
    max_restarts = json.get("max_restarts")
    validate = json.get("validate")
    return jobs.capture(
        tag, seconds, minutes, hours, force_restart, max_restarts, validate
    )


@jobs_blueprint.route("/session", methods=["POST"])
@jsendify_response
def session() -> str:
    json = request.get_json()
    tag = json.get("tag")
    seconds = json.get("seconds")
    minutes = json.get("minutes")
    hours = json.get("hours")
    force_restart = json.get("force_restart")
    max_restarts = json.get("max_restarts")
    validate = json.get("validate")
    return jobs.session(
        tag, seconds, minutes, hours, force_restart, max_restarts, validate
    )
