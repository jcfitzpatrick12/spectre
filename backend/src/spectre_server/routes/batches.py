# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from flask import Blueprint, request, url_for, Response
from os.path import basename

from ..services import batches
from ._datetimes import validate_date, get_date_from_batch_file_path
from ._format_responses import jsendify_response, serve_from_directory


batches_blueprint = Blueprint("batches", __name__, url_prefix="/spectre-data/batches")


def get_batch_file_endpoint(
    batch_file_path: str,
) -> str:
    """Return the URL endpoint corresponding to the input batch file path,"""
    batch_file_date = get_date_from_batch_file_path(batch_file_path)
    return url_for("batches.get_batch_file", 
                    base_file_name=basename(batch_file_path),
                    year=batch_file_date.year,
                    month=batch_file_date.month,
                    day=batch_file_date.day,
                    _external=True)


def get_batch_file_endpoints(
    batch_file_paths: list[str]
) -> list[str]:
    """Return the URL endpoints corresponding to the input batch file paths."""
    return [get_batch_file_endpoint(batch_file) for batch_file in batch_file_paths]
    
    
@batches_blueprint.route("/<int:year>/<int:month>/<int:day>/<string:base_file_name>", methods=["GET"])
@jsendify_response
def get_batch_file(
    year: int,
    month: int,
    day: int,
    base_file_name: str
) -> Response:
    validate_date(year, month, day)
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
) -> str:
    validate_date(year, month, day)
    batch_file_path = batches.delete_batch_file(base_file_name, year, month, day)
    return get_batch_file_endpoint(batch_file_path)


@batches_blueprint.route("/<int:year>/<int:month>/<int:day>", methods=["GET"])
@jsendify_response
def get_batch_files_year_month_day(
    year: int,
    month: int,
    day: int
) -> list[str]:
    tags       = request.args.getlist("tag")
    extensions = request.args.getlist("extension")
    validate_date(year, month, day)
    batch_files = batches.get_batch_files(tags, extensions, year=year, month=month, day=day)
    return get_batch_file_endpoints(batch_files)


@batches_blueprint.route("/<int:year>/<int:month>", methods=["GET"])
@jsendify_response
def get_batch_files_year_month(
    year: int,
    month: int,
) -> list[str]:
    tags       = request.args.getlist("tag")
    extensions = request.args.getlist("extension")
    validate_date(year, month)
    batch_files = batches.get_batch_files(tags, extensions, year=year, month=month)
    return get_batch_file_endpoints(batch_files)



@batches_blueprint.route("/<int:year>", methods=["GET"])
@jsendify_response
def get_batch_files_year(
    year: int,
) -> list[str]:
    tags       = request.args.getlist("tag")
    extensions = request.args.getlist("extension")
    validate_date(year)
    batch_files = batches.get_batch_files(tags, extensions, year=year)
    return get_batch_file_endpoints(batch_files)


@batches_blueprint.route("/", methods=["GET"])
@jsendify_response
def get_batch_files(
) -> list[str]:
    tags       = request.args.getlist("tag")
    extensions = request.args.getlist("extension")
    batch_files = batches.get_batch_files(tags, extensions)
    return get_batch_file_endpoints(batch_files)


@batches_blueprint.route("/<int:year>/<int:month>/<int:day>", methods=["DELETE"])
@jsendify_response
def delete_batch_files_year_month_day(
    year: int,
    month: int,
    day: int
) -> list[str]:
    extensions = request.args.getlist("extension")
    tags       = request.args.getlist("tag")
    validate_date(year, month, day)
    batch_files =  batches.delete_batch_files(tags,
                                              extensions,
                                              year,
                                              month,
                                              day)
    return get_batch_file_endpoints(batch_files)


@batches_blueprint.route("/<int:year>/<int:month>", methods=["DELETE"])
@jsendify_response
def delete_batch_files_year_month(
    year: int,
    month: int,
) -> list[str]:
    extensions = request.args.getlist("extension")
    tags       = request.args.getlist("tag")
    validate_date(year, month)
    batch_files =  batches.delete_batch_files(tags,
                                              extensions,
                                              year,
                                              month)
    return get_batch_file_endpoints(batch_files)


@batches_blueprint.route("/<int:year>", methods=["DELETE"])
@jsendify_response
def delete_batch_files_year(
    year: int,
) -> list[str]:
    extensions = request.args.getlist("extension")
    tags       = request.args.getlist("tag")
    validate_date(year)
    batch_files =  batches.delete_batch_files(tags,
                                              extensions,
                                              year)
    return get_batch_file_endpoints(batch_files)


@batches_blueprint.route("/", methods=["DELETE"])
@jsendify_response
def delete_batch_files(
) -> list[str]:
    extensions = request.args.getlist("extension")
    tags       = request.args.getlist("tag")
    batch_files =  batches.delete_batch_files(tags,
                                              extensions)
    return get_batch_file_endpoints(batch_files)

   

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
def get_tags_year_month_day(
    year: int,
    month: int,
    day: int
) -> list[str]:
    validate_date(year, month, day)
    return batches.get_tags(year,
                            month,
                            day)
    
@batches_blueprint.route("/<int:year>/<int:month>/tags", methods=["GET"])
@jsendify_response
def get_tags_year_month(
    year: int,
    month: int,
) -> list[str]:
    validate_date(year, month)
    return batches.get_tags(year,
                            month)
    
@batches_blueprint.route("/<int:year>/tags", methods=["GET"])
@jsendify_response
def get_tags_year(
    year: int,
) -> list[str]:
    validate_date(year)
    return batches.get_tags(year)
    
    
@batches_blueprint.route("/tags", methods=["GET"])
@jsendify_response
def get_tags(
) -> list[str]:
    return batches.get_tags()


@batches_blueprint.route("/plots", methods=["PUT"])
@jsendify_response
def create_plot(
) -> str:
    json = request.get_json()
    # Data from multiple batch files can be compared, by passing extra `tags` through the request body.
    tags         = json.get("tags")
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
    batch_file  =  batches.create_plot(tags,
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
    return get_batch_file_endpoint(batch_file)

                   
