# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import Blueprint, request

from spectre_server.services import test
from spectre_server.routes import jsendify_response


test_blueprint = Blueprint("get", __name__)

@test_blueprint.route("/test/analytical")
@jsendify_response
def analytical():
    payload = request.get_json()
    tag = payload.get("tag")
    absolute_tolerance = payload.get("absolute_tolerance")
    return test.analytical(tag,
                           absolute_tolerance)