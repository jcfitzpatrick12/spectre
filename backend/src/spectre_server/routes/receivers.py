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


@receivers_blueprint.route("/<string:receiver_name>", methods=["GET"])
@jsendify_response
def query_for(receiver_name: str
):
    query = request.args.get("query", type = str)
    return receivers.query_for(receiver_name, 
                               query,
                               mode = None)

@receivers_blueprint.route("/<string:receiver_name>/<string:mode>", methods=["GET"])
@jsendify_response
def get_for_in_mode(receiver_name: str,
                    mode: str
):
    query = request.args.get("query", type = str)
    return receivers.query_for(receiver_name, 
                               query,
                               mode = mode)


