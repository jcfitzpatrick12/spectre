# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from os.path import basename
from flask import Blueprint, request, url_for

from spectre_server.services import callisto
from spectre_server.routes._format_responses import jsendify_response

callisto_blueprint = Blueprint("callisto", __name__)


@callisto_blueprint.route("/instrument-codes", methods=["GET"])
@jsendify_response
def get_instrument_codes(
) -> list[str]:
    return callisto.get_instrument_codes()


@callisto_blueprint.route("/batches", methods=["POST"])
@jsendify_response
def download(
) -> list[str]:
    json = request.get_json()
    instrument_code = json.get("instrument_code")
    year            = json.get("year")
    month           = json.get("month")
    day             = json.get("day")
    batch_files, start_date = callisto.download_callisto_data(instrument_code,
                                                              year,
                                                              month,
                                                              day)
    resource_endpoints = []
    for batch_file in batch_files:
        resource_endpoint =  url_for("batches.get_batch_file",
                                     year=year,
                                     month=month,
                                     day=day,
                                     file_name=basename(batch_file),
                                     _external=True)
        resource_endpoints.append(resource_endpoint)
    return resource_endpoints
