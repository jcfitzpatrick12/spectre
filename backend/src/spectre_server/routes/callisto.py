# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from flask import Blueprint, request

from spectre_server.services import callisto
from spectre_server.routes import jsendify_response


callisto_blueprint = Blueprint("callisto", __name__)

@callisto_blueprint.route("/instrument-codes", methods=["GET"])
@jsendify_response
def get_instrument_codes():
    return callisto.get_instrument_codes()


@callisto_blueprint.route("/download", methods=["POST"])
@jsendify_response
def download():
    payload = request.get_json()
    instrument_code = payload.get("instrument_code")
    year = payload.get("year")
    month = payload.get("month")
    day = payload.get("day")
    return callisto.download(instrument_code,
                             year,
                             month,
                             day)