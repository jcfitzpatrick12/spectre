# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from flask import Blueprint, request

from spectre_server.services import batches
from spectre_server.routes._format_responses import jsendify_response


batches_blueprint = Blueprint("batches", __name__)


@batches_blueprint.route("/<string:tag>", methods=["PUT"])
@jsendify_response
def create_plot(
    tag: str
) -> str:
    json = request.get_json()
    # Data from multiple batch files can be compared, by passing extra `tags` through the request body.
    tags         = [tag] + json.get("tags")
    figsize_x    = json.get("figsize_x")
    figsize_y    = json.get("figsize_y")
    obs_date     = json.get("obs_date")
    start_time   = json.get("start_time")
    end_time     = json.get("end_time")
    lower_freq   = json.get("lower_freq")
    upper_freq   = json.get("upper_freq")
    log_norm     = json.get("log_norm")
    dBb          = json.get("dBb")
    vmin         = json.get("vmin")
    vmax         = json.get("vmax")    
    
    # Handle the edge cases for figsize being specified.
    figsize_x_specified = figsize_x is not None
    figsize_y_specifed = figsize_y is not None
    if figsize_x_specified ^ figsize_y_specifed:
        raise ValueError("Either both of `figsize_x` and `figsize_y` must be specified, or neither.")
    elif figsize_x_specified and figsize_y_specifed:
        figsize = (figsize_x, figsize_y)
    else:
        figsize = (15, 8)
        
    return batches.create_plot(tags,
                               figsize,
                               obs_date,
                               start_time,
                               end_time,
                               lower_freq=lower_freq,
                               upper_freq=upper_freq,
                               log_norm=log_norm,
                               dBb=dBb,
                               vmin=vmin,
                               vmax=vmax)


@batches_blueprint.route("/<string:tag>", methods=["GET"])
@jsendify_response
def get_batch_files_for_tag(
    tag: str
) -> list[str]:
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
def delete_batch_files(
    tag: str
) -> list[str]:
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
def get_analytical_test_results(
    tag: str
) -> dict[str, dict[str, bool | dict[float, bool]]]:
    absolute_tolerance = request.args.get("absolute_tolerance", type = float, default=1e-5)
    return batches.get_analytical_test_results(tag,
                                               absolute_tolerance)


@batches_blueprint.route("/tags", methods=["GET"])
@jsendify_response
def get_tags(
) -> list[str]:
    year  = request.args.get("year" , type = int)
    month = request.args.get("month", type = int)
    day   = request.args.get("day"  , type = int)
    return batches.get_tags(year,
                            month,
                            day)