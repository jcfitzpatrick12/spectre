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

@receivers_blueprint.route("/<string:receiver_name>/specifications", methods=["GET"])
@jsendify_response
def get_specifications(receiver_name: str
):
    return receivers.get_specifications(receiver_name)


@receivers_blueprint.route("/<string:receiver_name>/type-template", methods=["GET"])
@jsendify_response
def get_type_template(receiver_name: str
):
    mode = request.args.get("mode")
    return receivers.get_type_template(receiver_name, 
                                       mode)



