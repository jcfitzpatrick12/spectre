# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from flask import Blueprint, request, url_for, Response
from os.path import basename
from typing import Optional

from ..services import batches
from ._datetimes import validate_date, get_date_from_batch_file_path
from ._format_responses import jsendify_response, serve_from_directory


batches_blueprint = Blueprint("batches", __name__, url_prefix="/spectre-data/batches")


def _get_batch_file_endpoint(
    batch_file_path: str,
) -> str:
    """Return the API endpoint corresponding to the batch file at the input path."""
    batch_file_date = get_date_from_batch_file_path(batch_file_path)
    return url_for("batches.get_batch_file", 
                    base_file_name=basename(batch_file_path),
                    year=batch_file_date.year,
                    month=batch_file_date.month,
                    day=batch_file_date.day,
                    _external=True)


def _get_batch_file_endpoints(
    batch_files: list[str],
    year: Optional[int]=None,
    month: Optional[int]=None,
    day: Optional[int]=None,
) -> list[str]:
    """Return the API endpoints to all batch files which exist in the container's file system."""
    validate_date(year, month, day)
    return [_get_batch_file_endpoint(batch_file) for batch_file in batch_files]
    
    
@batches_blueprint.route("/<int:year>/<int:month>/<int:day>/<string:base_file_name>", methods=["GET"])
@jsendify_response
def get_batch_file(
    year: int,
    month: int,
    day: int,
    base_file_name: str
) -> Response:
    return serve_from_directory(batches.get_batch_file(base_file_name,
                                                       year,
                                                       month,
                                                       day))
    

@batches_blueprint.route("/<int:year>/<int:month>/<int:day>/<string:base_file_name>", methods=["DELETE"])
@jsendify_response
def delete_batch_file(
    year: int,
    month: int,
    day: int,
    base_file_name: str
) -> Response:
    batch_file_path = batches.delete_batch_file(base_file_name, year, month, day)
    return _get_batch_file_endpoint(batch_file_path, year, month, day)


@batches_blueprint.route("/<int:year>/<int:month>/<int:day>", methods=["GET"])
@jsendify_response
def get_batch_files_year_month_day(
    year: int,
    month: int,
    day: int
) -> list[str]:
    tags       = request.args.getlist("tag")
    extensions = request.args.getlist("extension")
    batch_files = batches.get_batch_files(tags, extensions, year=year, month=month, day=day)
    return _get_batch_file_endpoints(batch_files, year=year, month=month, day=day)


@batches_blueprint.route("/<int:year>/<int:month>", methods=["GET"])
@jsendify_response
def get_batch_files_year_month(
    year: int,
    month: int,
) -> list[str]:
    tags       = request.args.getlist("tag")
    extensions = request.args.getlist("extension")
    batch_files = batches.get_batch_files(tags, extensions, year=year, month=month)
    return _get_batch_file_endpoints(batch_files, year=year, month=month)



@batches_blueprint.route("/<int:year>", methods=["GET"])
@jsendify_response
def get_batch_files_year(
    year: int,
) -> list[str]:
    tags       = request.args.getlist("tag")
    extensions = request.args.getlist("extension")
    batch_files = batches.get_batch_files(tags, extensions, year=year)
    return _get_batch_file_endpoints(batch_files, year=year)


@batches_blueprint.route("/", methods=["GET"])
@jsendify_response
def get_batch_files(
) -> list[str]:
    tags       = request.args.getlist("tag")
    extensions = request.args.getlist("extension")
    batch_files = batches.get_batch_files(tags, extensions)
    return _get_batch_file_endpoints(batch_files)


@batches_blueprint.route("/<int:year>/<int:month>/<int:day>", methods=["DELETE"])
@jsendify_response
def delete_batch_files(
    year: int,
    month: int,
    day: int
) -> list[str]:
    extensions = request.args.getlist("extension")
    tags       = request.args.getlist("tag")


    batch_files =  batches.delete_batch_files(tags,
                                              extensions,
                                              year,
                                              month,
                                              day)

    
    return _get_batch_file_endpoints(batch_files, year, month, day)

   

@batches_blueprint.route("/<int:year>/<int:month>/<int:day>/<string:base_file_name>/analytical-test-results", methods=["GET"])
@jsendify_response
def get_analytical_test_results(
    year: int,
    month: int,
    day: int,
    base_file_name: str,
) -> dict[str, bool | dict[float, bool]]:
    absolute_tolerance = request.args.get("absolute_tolerance", type = float, default=1e-5)
    return batches.get_analytical_test_results(year,
                                               month,
                                               day,
                                               base_file_name,
                                               absolute_tolerance)


@batches_blueprint.route("/<int:year>/<int:month>/<int:day>/tags", methods=["GET"])
@jsendify_response
def get_tags(
    year: int,
    month: int,
    day: int
) -> list[str]:
    return batches.get_tags(year,
                            month,
                            day)


@batches_blueprint.route("/plots/<string:tag>", methods=["PUT"])
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
    figsize_y_specified = figsize_y is not None
    if figsize_x_specified ^ figsize_y_specified:
        raise ValueError("Either both of `figsize_x` and `figsize_y` must be specified, or neither.")
    elif figsize_x_specified and figsize_y_specified:
        figsize = (figsize_x, figsize_y)
    else:
        # If nothing is specified, set an arbitrary default value.
        figsize = (15, 8)

    # Create the plot and return the name of the batch file containing the plot.    
    batch_file, batch_start_date =  batches.create_plot(tags,
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
    return _get_batch_file_endpoint(batch_file,
                                    year=batch_start_date.year,
                                    month=batch_start_date.month,
                                    day=batch_start_date.day)

                   
