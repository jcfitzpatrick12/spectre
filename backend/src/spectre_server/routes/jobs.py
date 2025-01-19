# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import Blueprint, request

from spectre_server.services import jobs
from spectre_server.routes._format_responses import jsendify_response


jobs_blueprint = Blueprint("jobs", __name__)


@jobs_blueprint.route("/capture", methods=["POST"])
@jsendify_response
def capture(
):
    json = request.get_json()
    tag           = json.get("tag")
    seconds       = json.get("seconds")
    minutes       = json.get("minutes")
    hours         = json.get("hours")
    force_restart = json.get("force_restart")
    return jobs.capture(tag,
                        seconds,
                        minutes,
                        hours,
                        force_restart)


@jobs_blueprint.route("/session", methods=["POST"])
@jsendify_response
def session(
):
    json          = request.get_json()
    tag           = json.get("tag")
    seconds       = json.get("seconds")
    minutes       = json.get("minutes")
    hours         = json.get("hours")
    force_restart = json.get("force_restart")
    return jobs.session(tag,
                        seconds,
                        minutes,
                        hours,
                        force_restart)