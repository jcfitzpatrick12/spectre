# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import Blueprint, request

from spectre_server.services import update
from spectre_server.routes import jsendify_response


update_blueprint = Blueprint("update", __name__)

@update_blueprint.route("/capture-config", methods=["POST"])
@jsendify_response
def capture_config():
    payload = request.get_json()
    tag = payload.get("tag")
    params = payload.get("params")
    force = payload.get("force")
    return update.capture_config(tag,
                                 params,
                                 force)


@update_blueprint.route("/fits-config", methods=["POST"])
@jsendify_response
def fits_config():
    payload = request.get_json()
    tag = payload.get("tag")
    params = payload.get("params")
    force = payload.get("force")
    return update.fits_config(tag,
                              params,
                              force)