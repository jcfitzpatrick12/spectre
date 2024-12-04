# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import Blueprint, request

from spectre_server.services import delete
from spectre_server.routes import jsendify_response

delete_blueprint = Blueprint("delete", __name__)

@delete_blueprint.route("/logs", methods=["POST"])
@jsendify_response
def logs():
    payload = request.get_json()
    process_type = payload.get("process_type")
    year = payload.get("year")
    month = payload.get("month")
    day = payload.get("day")
    return delete.logs(process_type,
                       year,
                       month,
                       day)