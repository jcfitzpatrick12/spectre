# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from flask import Blueprint, request, url_for, Response
from os.path import basename

from ..services import logs
from ._format_responses import jsendify_response, serve_from_directory
from ._utils import get_date_from_log_file_path, validate_date, is_true


logs_blueprint = Blueprint("logs", __name__, url_prefix="/spectre-data/logs")


def _get_log_file_endpoint(
    log_file_path: str,
) -> str:
    """Return the URL endpoint corresponding to the log file at the input path."""
    return url_for(
        "logs.get_log",
        file_name=basename(log_file_path),
        _external=True,
    )


def _get_log_file_endpoints(log_file_paths: list[str]) -> list[str]:
    """Return the URL endpoints corresponding to the input log file paths."""
    return [_get_log_file_endpoint(log_file) for log_file in log_file_paths]


@logs_blueprint.route("/<string:file_name>", methods=["GET"])
@jsendify_response
def get_log(file_name: str) -> Response:
    return serve_from_directory(logs.get_log(file_name))


@logs_blueprint.route("/<string:file_name>/raw", methods=["GET"])
@jsendify_response
def get_log_raw(file_name: str) -> str:
    return logs.get_log_raw(file_name)


@logs_blueprint.route("/", methods=["GET"])
@jsendify_response
def get_logs() -> list[str]:
    process_types = request.args.getlist("process_type")
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    day = request.args.get("day", type=int)
    validate_date(year, month, day)
    log_files = logs.get_logs(process_types, year=year, month=month, day=day)
    return _get_log_file_endpoints(log_files)


@logs_blueprint.route("/<string:file_name>", methods=["DELETE"])
@jsendify_response
def delete_log(file_name: str) -> str:
    dry_run = request.args.get("dry_run", type=is_true, default=False)
    log_file = logs.delete_log(file_name, dry_run=dry_run)
    return _get_log_file_endpoint(log_file)


@logs_blueprint.route("/", methods=["DELETE"])
@jsendify_response
def delete_logs() -> list[str]:
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    day = request.args.get("day", type=int)
    dry_run = request.args.get("dry_run", type=is_true, default=False)
    validate_date(year, month, day)
    process_types = request.args.getlist("process_type")

    log_files = logs.delete_logs(
        process_types, year=year, month=month, day=day, dry_run=dry_run
    )

    return _get_log_file_endpoints(log_files)
