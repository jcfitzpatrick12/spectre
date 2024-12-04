# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from flask import Blueprint, request

from spectre_server.services import create
from spectre_server.routes import jsendify_response

create_blueprint = Blueprint("create", __name__)

@create_blueprint.route("/fits-config", methods=["POST"])
@jsendify_response
def fits_config():
    payload = request.get_json()
    tag = payload.get("tag")
    params = payload.get("params")
    force = payload.get("force")
    return create.fits_config(tag, 
                              params,
                              force)
    

@create_blueprint.route("/capture-config", methods=["POST"])
@jsendify_response
def capture_config():
    payload = request.get_json()
    tag = payload.get("tag")
    receiver_name = payload.get("receiver_name")
    mode = payload.get("mode")
    params = payload.get("params")
    force = payload.get("force")
    return create.capture_config(tag, 
                                 receiver_name,
                                 mode,
                                 params,
                                 force)