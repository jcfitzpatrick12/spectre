# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


import flask
import os

from ..services import logs as services
from ._format_responses import jsendify_response, serve_from_directory
from ._utils import validate_date, is_true


logs_blueprint = flask.Blueprint("logs", __name__, url_prefix="/spectre-data/logs")


def _get_log_file_endpoint(
    log_file_path: str,
) -> str:
    """Return the URL endpoint corresponding to the log file at the input path."""
    return flask.url_for(
        "logs.get_log",
        file_name=os.path.basename(log_file_path),
    )


def _get_log_file_endpoints(log_file_paths: list[str]) -> list[str]:
    """Return the URL endpoints corresponding to the input log file paths."""
    return [_get_log_file_endpoint(log_file) for log_file in log_file_paths]


@logs_blueprint.route("/<string:file_name>", methods=["GET"])
def get_log(file_name: str) -> flask.Response:
    return serve_from_directory(services.get_log(file_name))


@logs_blueprint.route("/<string:file_name>/raw", methods=["GET"])
@jsendify_response
def get_log_raw(file_name: str) -> str:
    return services.get_log_raw(file_name)


@logs_blueprint.route("/", methods=["GET"])
@jsendify_response
def get_logs() -> list[str]:
    process_types = flask.request.args.getlist("process_type")
    year = flask.request.args.get("year", type=int)
    month = flask.request.args.get("month", type=int)
    day = flask.request.args.get("day", type=int)
    validate_date(year, month, day)
    log_files = services.get_logs(process_types, year=year, month=month, day=day)
    return _get_log_file_endpoints(log_files)


@logs_blueprint.route("/<string:file_name>", methods=["DELETE"])
@jsendify_response
def delete_log(file_name: str) -> str:
    dry_run = flask.request.args.get("dry_run", type=is_true, default=False)
    log_file = services.delete_log(file_name, dry_run=dry_run)
    return _get_log_file_endpoint(log_file)


@logs_blueprint.route("/", methods=["DELETE"])
@jsendify_response
def delete_logs() -> list[str]:
    year = flask.request.args.get("year", type=int)
    month = flask.request.args.get("month", type=int)
    day = flask.request.args.get("day", type=int)
    dry_run = flask.request.args.get("dry_run", type=is_true, default=False)
    validate_date(year, month, day)
    process_types = flask.request.args.getlist("process_type")

    log_files = services.delete_logs(
        process_types, year=year, month=month, day=day, dry_run=dry_run
    )

    return _get_log_file_endpoints(log_files)
