# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from flask import Blueprint, request

from spectre_server.services import batches
from spectre_server.routes._format_responses import jsendify_response


batches_blueprint = Blueprint("batches", __name__)


@batches_blueprint.route("", methods=["GET"])
@jsendify_response
def get_batch_files():
    tags       = request.args.getlist("tag")
    extensions = request.args.getlist("extension")
    year       = request.args.get("year" , type = int)
    month      = request.args.get("month", type = int)
    day        = request.args.get("day"  , type = int)
    return batches.get_batch_files(tags,
                                  extensions, 
                                  year,
                                  month,
                                  day)


@batches_blueprint.route("/<string:tag>", methods=["GET"])
@jsendify_response
def get_batch_files_for_tag(tag: str):
    extensions = request.args.getlist("extension")
    year       = request.args.get("year" , type = int)
    month      = request.args.get("month", type = int)
    day        = request.args.get("day"  , type = int)
    return batches.get_batch_files_for_tag(tag,
                                          extensions, 
                                          year,
                                          month,
                                          day)


@batches_blueprint.route("/<string:tag>", methods=["DELETE"])
@jsendify_response
def delete_batch_files(tag: str):
    extensions = request.args.getlist("extension")
    year  = request.args.get("year" , type = int)
    month = request.args.get("month", type = int)
    day   = request.args.get("day"  , type = int)
    return batches.delete_batch_files(tag,
                                     extensions, 
                                     year,
                                     month,
                                     day)


@batches_blueprint.route("/<string:tag>/analytical-test-results", methods=["GET"])
@jsendify_response
def get_analytical_test_results(tag: str):
    absolute_tolerance = request.args.get("absolute_tolerance", type = float)
    return batches.get_analytical_test_results(tag,
                                              absolute_tolerance)


@batches_blueprint.route("/tags", methods=["GET"])
@jsendify_response
def get_tags():
    year  = request.args.get("year" , type = int)
    month = request.args.get("month", type = int)
    day   = request.args.get("day"  , type = int)
    return batches.get_tags(year,
                           month,
                           day)