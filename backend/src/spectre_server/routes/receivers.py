# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import Blueprint, request

from spectre_server.services import receivers
from spectre_server.routes import jsendify_response


receivers_blueprint = Blueprint("receivers", __name__)

@receivers_blueprint.route("", methods=["GET"])
@jsendify_response
def get_receivers(
):
    return receivers.list_all_receiver_names()


@receivers_blueprint.route("/<string:receiver_name>/modes", methods=["GET"])
@jsendify_response
def get_modes(receiver_name: str
):
    return receivers.get_modes(receiver_name)


@receivers_blueprint.route("/<string:receiver_name>/specs", methods=["GET"])
@jsendify_response
def get_specs(receiver_name: str
):
    return receivers.get_specs(receiver_name)


@receivers_blueprint.route("/<string:receiver_name>/capture-template", methods=["GET"])
@jsendify_response
def get_type_template(receiver_name: str
):
    receiver_mode = request.args.get("receiver_mode")
    return receivers.get_capture_template(receiver_name, 
                                          receiver_mode)



