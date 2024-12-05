# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import Blueprint, request

from spectre_server.old_services import web_fetch
from spectre_server.old_routes import jsendify_response

web_fetch_blueprint = Blueprint("web-fetch", __name__)

@web_fetch_blueprint.route("/callisto")
@jsendify_response
def callisto():
    payload = request.get_json()
    instrument_code = payload.get("instrument_code")
    year = payload.get("year")
    month = payload.get("month")
    day = payload.get("day")
    web_fetch.callisto(instrument_code,
                       year,
                       month,
                       day)