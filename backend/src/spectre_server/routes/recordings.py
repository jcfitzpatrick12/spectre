# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import flask

from ..services import recordings as services
from ._format_responses import jsendify_response


recordings_blueprint = flask.Blueprint("recordings", __name__, url_prefix="/recordings")


@recordings_blueprint.route("/signal", methods=["POST"])
@jsendify_response
def signal() -> int:
    json = flask.request.get_json()
    tags = json.get("tags")
    duration = json.get("duration")
    force_restart = json.get("force_restart")
    max_restarts = json.get("max_restarts")
    validate = json.get("validate")
    return services.signal(tags, duration, force_restart, max_restarts, validate)


@recordings_blueprint.route("/spectrogram", methods=["POST"])
@jsendify_response
def spectrograms() -> int:
    json = flask.request.get_json()
    tags = json.get("tags")
    duration = json.get("duration")
    force_restart = json.get("force_restart")
    max_restarts = json.get("max_restarts")
    validate = json.get("validate")
    return services.spectrograms(tags, duration, force_restart, max_restarts, validate)
