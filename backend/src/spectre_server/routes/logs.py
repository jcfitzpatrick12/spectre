# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from flask import Blueprint, request, url_for, Response
from os.path import basename

from ..services import logs
from ._format_responses import jsendify_response, serve_from_directory
from ._datetimes import get_date_from_log_file_path, validate_date


logs_blueprint = Blueprint("logs", __name__, url_prefix="/spectre-data/logs")


def _get_log_file_endpoint(
    log_file_path: str,
) -> str:
    """Return the URL endpoint corresponding to the log file at the input path."""
    log_file_date = get_date_from_log_file_path(log_file_path)
    return url_for("logs.get_log", 
                    base_file_name=basename(log_file_path),
                    year=log_file_date.year,
                    month=log_file_date.month,
                    day=log_file_date.day,
                    _external=True)


def _get_log_file_endpoints(
    log_file_paths: list[str]
) -> list[str]:
    """Return the URL endpoints corresponding to the input log file paths."""
    return [_get_log_file_endpoint(log_file) for log_file in log_file_paths]


@logs_blueprint.route("/<int:year>/<int:month>/<int:day>/<string:base_file_name>", methods=["GET"])
@jsendify_response
def get_log(
    year: int,
    month: int,
    day: int,
    base_file_name: str
) -> Response:
    validate_date(year, month, day)
    return serve_from_directory(logs.get_log(base_file_name,
                                             year,
                                             month,
                                             day))


@logs_blueprint.route("/<int:year>/<int:month>/<int:day>/<string:base_file_name>/raw", methods=["GET"])
@jsendify_response
def get_log_raw(
    year: int,
    month: int,
    day: int,
    base_file_name: str
) -> str:
    validate_date(year, month, day)
    return logs.get_log_raw(base_file_name,
                            year,
                            month,
                            day)


@logs_blueprint.route("/<int:year>/<int:month>/<int:day>", methods=["GET"])
@jsendify_response
def get_logs_year_month_day(
    year: int,
    month: int,
    day: int
) -> list[str]:
    process_types = request.args.getlist("process_type")
    validate_date(year, month, day)
    log_files = logs.get_logs(process_types,
                              year,
                              month,
                              day)
    return _get_log_file_endpoints(log_files)


@logs_blueprint.route("/<int:year>/<int:month>", methods=["GET"])
@jsendify_response
def get_logs_year_month(
    year: int,
    month: int,
) -> list[str]:
    process_types = request.args.getlist("process_type")
    validate_date(year, month)
    log_files = logs.get_logs(process_types,
                              year,
                              month)
    return _get_log_file_endpoints(log_files)


@logs_blueprint.route("/<int:year>", methods=["GET"])
@jsendify_response
def get_logs_year(
    year: int,
) -> list[str]:
    process_types = request.args.getlist("process_type")
    validate_date(year)
    log_files = logs.get_logs(process_types,
                              year)
    return _get_log_file_endpoints(log_files)


@logs_blueprint.route("/", methods=["GET"])
@jsendify_response
def get_logs(
) -> list[str]:
    process_types = request.args.getlist("process_type")
    log_files = logs.get_logs(process_types)
    return _get_log_file_endpoints(log_files)
                         

@logs_blueprint.route("/<int:year>/<int:month>/<int:day>/<string:base_file_name>", methods=["DELETE"])
@jsendify_response
def delete_log(
    year: int,
    month: int,
    day: int,
    base_file_name: str
) -> str:
    validate_date(year, month, day)
    log_file = logs.delete_log(base_file_name,
                               year,
                               month,
                               day)
    return _get_log_file_endpoint(log_file)


@logs_blueprint.route("/<int:year>/<int:month>/<int:day>", methods=["DELETE"])
@jsendify_response
def delete_logs_year_month_day(
    year: int,
    month: int,
    day: int
) -> list[str]:
    validate_date(year, month, day)
    process_types = request.args.getlist("process_type")
    
    log_files =  logs.delete_logs(process_types,
                                  year,
                                  month,
                                  day)
    
    return _get_log_file_endpoints(log_files)


@logs_blueprint.route("/<int:year>/<int:month>", methods=["DELETE"])
@jsendify_response
def delete_logs_year_month(
    year: int,
    month: int,
) -> list[str]:
    process_types = request.args.getlist("process_type")
    validate_date(year, month)
    log_files =  logs.delete_logs(process_types,
                                  year,
                                  month)
    
    return _get_log_file_endpoints(log_files)


@logs_blueprint.route("/<int:year>", methods=["DELETE"])
@jsendify_response
def delete_logs_year(
    year: int,
) -> list[str]:
    process_types = request.args.getlist("process_type")
    validate_date(year)
    log_files =  logs.delete_logs(process_types,
                                  year)
    
    return _get_log_file_endpoints(log_files)


@logs_blueprint.route("/", methods=["DELETE"])
@jsendify_response
def delete_logs(
) -> list[str]:
    process_types = request.args.getlist("process_type")
    
    log_files =  logs.delete_logs(process_types)
    return _get_log_file_endpoints(log_files)
