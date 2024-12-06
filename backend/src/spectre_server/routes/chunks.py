# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from flask import Blueprint, request

from spectre_server.services import chunks
from spectre_server.routes import jsendify_response


chunks_blueprint = Blueprint("chunks", __name__)


@chunks_blueprint.route("", methods=["GET"])
@jsendify_response
def get_chunk_files():
    tags = request.args.getlist("tag")
    extensions = request.args.getlist("extension")
    year = request.args.get("year", type = int)
    month = request.args.get("month", type = int)
    day = request.args.get("day", type = int)
    return chunks.get_chunk_files(tags,
                                  extensions, 
                                  year,
                                  month,
                                  day)


@chunks_blueprint.route("/<string:tag>", methods=["GET"])
@jsendify_response
def get_chunk_files_for_tag(tag: str):
    extensions = request.args.getlist("extension")
    year = request.args.get("year", type = int)
    month = request.args.get("month", type = int)
    day = request.args.get("day", type = int)
    return chunks.get_chunk_files_for_tag(tag,
                                          extensions, 
                                          year,
                                          month,
                                          day)


@chunks_blueprint.route("/<string:tag>", methods=["DELETE"])
@jsendify_response
def delete_chunk_files(tag: str):
    extensions = request.args.getlist("extension")
    year = request.args.get("year", type = int)
    month = request.args.get("month", type = int)
    day = request.args.get("day", type = int)
    return chunks.delete_chunk_files(tag,
                                     extensions, 
                                     year,
                                     month,
                                     day)


@chunks_blueprint.route("/<string:tag>/analytical-test-results", methods=["GET"])
@jsendify_response
def get_analytical_test_results(tag: str):
    absolute_tolerance = request.args.get("absolute_tolerance", type = float)
    return chunks.get_analytical_test_results(tag,
                                              absolute_tolerance)


@chunks_blueprint.route("/tags", methods=["GET"])
@jsendify_response
def get_tags():
    year = request.args.get("year", type = int)
    month = request.args.get("month", type = int)
    day = request.args.get("day", type = int)
    return chunks.get_tags(year,
                           month,
                           day)