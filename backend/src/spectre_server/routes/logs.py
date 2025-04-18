# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from flask import Blueprint, request, url_for, Response
from os.path import basename

from spectre_server.services import logs
from spectre_server.routes._format_responses import jsendify_response, serve_from_directory


logs_blueprint = Blueprint("logs", __name__, url_prefix="/spectre-data/logs")


@logs_blueprint.route("/<int:year>/<int:month>/<int:day>/<string:base_file_name>", methods=["GET"])
@jsendify_response
def get_log(
    year: int,
    month: int,
    day: int,
    base_file_name: str
) -> Response:
    return serve_from_directory(logs.get_log(year,
                                             month,
                                             day,
                                             base_file_name))


@logs_blueprint.route("/<int:year>/<int:month>/<int:day>/<string:base_file_name>/raw", methods=["GET"])
@jsendify_response
def get_log_raw(
    year: int,
    month: int,
    day: int,
    base_file_name: str
) -> str:
    return logs.get_log_raw(year,
                            month,
                            day,
                            base_file_name)


@logs_blueprint.route("/<int:year>/<int:month>/<int:day>", methods=["GET"])
@jsendify_response
def get_logs(
    year: int,
    month: int,
    day: int
) -> list[str]:
    process_types = request.args.getlist("process_type")
    log_files = logs.get_logs(year,
                              month,
                              day,
                              process_types)

    resource_endpoints = []
    for log_file in log_files:
        resource_endpoint = url_for("logs.get_log",
                                    year=year,
                                    month=month,
                                    day=day,
                                    base_file_name=basename(log_file),
                                    _external=True)
        resource_endpoints.append(resource_endpoint)

    return resource_endpoints
                         

@logs_blueprint.route("/<int:year>/<int:month>/<int:day>/<string:base_file_name>", methods=["DELETE"])
@jsendify_response
def delete_log(
    year: int,
    month: int,
    day: int,
    base_file_name: str
) -> str:
    log_file = logs.delete_log(year,
                               month,
                               day,
                               base_file_name)
    return url_for("logs.get_log",
                   year=year,
                   month=month,
                   day=day,
                   base_file_name = basename(log_file),
                   _external=True)


@logs_blueprint.route("/<int:year>/<int:month>/<int:day>", methods=["DELETE"])
@jsendify_response
def delete_logs(
    year: int,
    month: int,
    day: int
) -> list[str]:
    process_types = request.args.getlist("process_type")
    
    log_files =  logs.delete_logs(year,
                                  month,
                                  day,
                                  process_types)

    resource_endpoints = []
    for log_file in log_files:
        resource_endpoint = url_for("logs.get_log",
                                    year=year,
                                    month=month,
                                    day=day,
                                    base_file_name=basename(log_file),
                                    _external=True)
        resource_endpoints.append(resource_endpoint)

    return resource_endpoints
