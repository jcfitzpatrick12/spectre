# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from flask import Blueprint, request

from ..services import callisto
from .batches import get_batch_file_endpoints
from ._format_responses import jsendify_response


callisto_blueprint = Blueprint("callisto", __name__, url_prefix="/callisto")


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

    batch_files, _ = callisto.download_callisto_data(instrument_code,
                                                     year,
                                                     month,
                                                     day)
    
    return get_batch_file_endpoints( batch_files )
