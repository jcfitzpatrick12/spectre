# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from flask import Blueprint, request

from spectre_server.services import capture
from spectre_server.routes import wrap_route

capture_blueprint = Blueprint("capture", __name__)


@capture_blueprint.route("/start", methods=["POST"])
@wrap_route
def start():
    data = request.get_json()
    tag = data.get("tag")
    seconds = data.get("seconds")
    minutes = data.get("minutes")
    hours = data.get("hours")
    force_restart = data.get("force_restart")
    return capture.start(tag,
                         seconds,
                         minutes,
                         hours,
                         force_restart)
