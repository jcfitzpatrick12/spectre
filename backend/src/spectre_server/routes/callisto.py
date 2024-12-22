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


@callisto_blueprint.route("/chunks", methods=["POST"])
@jsendify_response
def download():
    json = request.get_json()
    instrument_code = json.get("instrument_code")
    year            = json.get("year")
    month           = json.get("month")
    day             = json.get("day")
    return callisto.download_callisto_data(instrument_code,
                                           year,
                                           month,
                                           day)