# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from flask import Blueprint, request, url_for
from os.path import basename

from ..services import batches
from ._format_responses import jsendify_response, serve_from_directory


batches_blueprint = Blueprint("batches", __name__, url_prefix="/spectre-data/batches")


@batches_blueprint.route("/<int:year>/<int:month>/<int:day>/<string:file_name>", methods=["GET"])
def get_batch_file(
    year: int,
    month: int,
    day: int,
    file_name: str
) -> str:
    return serve_from_directory(batches.get_batch_file(year,
                                                       month,
                                                       day,
                                                       file_name))


@batches_blueprint.route("/<int:year>/<int:month>/<int:day>", methods=["GET"])
@jsendify_response
def get_batch_files(
    year: int,
    month: int,
    day: int
) -> list[str]:
    extensions = request.args.getlist("extension")
    tags       = request.args.getlist("tag")
    
    # Get the absolute file paths w.r.t. the container's file system.
    batch_files = batches.get_batch_files(year,
                                          month,
                                          day,
                                          tags,
                                          extensions)
    # Convert the absolute file path's to endpoints the user can use to get each file.
    resource_endpoints = []
    for batch_file in batch_files:
         resource_endpoint = url_for("batches.get_batch_file", 
                                     year=year,
                                     month=month,
                                     day=day,
                                     file_name=basename(batch_file),
                                     _external=True)
         resource_endpoints.append( resource_endpoint  )
    return resource_endpoints


@batches_blueprint.route("/<int:year>/<int:month>/<int:day>/<string:file_name>", methods=["DELETE"])
@jsendify_response
def delete_batch_file(
    year: int,
    month: int,
    day: int,
    file_name: str
) -> str:
    # Delete the batch file, and get the absolute file path of the file deleted w.r.t. the container's file system.
    batch_file = batches.delete_batch_file(year,
                                           month,
                                           day,
                                           file_name)
    # Convert the absolute path into the endpoint for the deleted resource.
    return url_for("batches.get_file",
                   year=year,
                   month=month,
                   day=day,
                   file_name=basename(batch_file),
                   _external=True)


@batches_blueprint.route("/<int:year>/<int:month>/<int:day>", methods=["DELETE"])
@jsendify_response
def delete_batch_files(
    year: int,
    month: int,
    day: int
) -> list[str]:
    extensions = request.args.getlist("extension")
    tags       = request.args.getlist("tag")

    # Delete each batch file, and get a list of absolute paths of each batch file which has been deleted w.r.t. the container's file system 
    batch_files =  batches.delete_batch_files(year,
                                              month,
                                              day,
                                              tags,
                                              extensions)

    # Convert the absolute file path's to endpoints the user can use to get each file.
    resource_endpoints = []
    for batch_file in batch_files:
         resource_endpoint = url_for("batches.delete_batch_file", 
                                     year=year,
                                     month=month,
                                     day=day,
                                     file_name=basename(batch_file),
                                     _external=True)
         resource_endpoints.append( resource_endpoint  )
    return resource_endpoints
   

@batches_blueprint.route("/analytical-test-results/<int:year>/<int:month>/<int:day>/<string:file_name>", methods=["GET"])
@jsendify_response
def get_analytical_test_results(
    year: int,
    month: int,
    day: int,
    file_name: str,
) -> dict[str, bool | dict[float, bool]]:
    absolute_tolerance = request.args.get("absolute_tolerance", type = float, default=1e-5)
    return batches.get_analytical_test_results(year,
                                               month,
                                               day,
                                               file_name,
                                               absolute_tolerance)


@batches_blueprint.route("/tags/<int:year>/<int:month>/<int:day>", methods=["GET"])
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
    figsize_y_specifed = figsize_y is not None
    if figsize_x_specified ^ figsize_y_specifed:
        raise ValueError("Either both of `figsize_x` and `figsize_y` must be specified, or neither.")
    elif figsize_x_specified and figsize_y_specifed:
        figsize = (figsize_x, figsize_y)
    else:
        # If nothing is specified, set an arbitrary default value.
        figsize = (15, 8)

    # Create the plot and return the name of the batch file containing the plot.    
    batch_file, batch_start_time =  batches.create_plot(tags,
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
    return url_for("batches.get_batch_file",
                   year=batch_start_time.year,
                   month=batch_start_time.month,
                   day=batch_start_time.day,
                   file_name=basename(batch_file),
                   _external=True)

                   
