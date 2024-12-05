# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import Blueprint, request

from spectre_server.services import jobs
from spectre_server.routes import jsendify_response


jobs_blueprint = Blueprint("jobs", __name__)


@jobs_blueprint.route("/capture", methods=["POST"])
@jsendify_response
def capture():
    payload = request.get_json()
    tag = payload.get("tag")
    seconds = payload.get("seconds")
    minutes = payload.get("minutes")
    hours = payload.get("hours")
    force_restart = payload.get("force_restart")
    return jobs.session(tag,
                        seconds,
                        minutes,
                        hours,
                        force_restart)


@jobs_blueprint.route("/session", methods=["POST"])
@jsendify_response
def session():
    payload = request.get_json()
    tag = payload.get("tag")
    seconds = payload.get("seconds")
    minutes = payload.get("minutes")
    hours = payload.get("hours")
    force_restart = payload.get("force_restart")
    return jobs.session(tag,
                        seconds,
                        minutes,
                        hours,
                        force_restart)