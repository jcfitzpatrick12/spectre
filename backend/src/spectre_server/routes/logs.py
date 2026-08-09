# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


import flask
import os

import spectre_server.core.logs

from ..services import logs as services
from ._format_responses import jsendify_response, serve_from_directory
from ._utils import is_true

logs_blueprint = flask.Blueprint("logs", __name__, url_prefix="/spectre-data/logs")


def _get_log_file_endpoint(
    log_file_path: str,
) -> str:
    """Return the URL endpoint corresponding to the log file at the input path."""
    return flask.url_for(
        "logs.get_log",
        file_name=os.path.basename(log_file_path),
        _external=True,
    )


def _get_log_file_endpoints(log_file_paths: list[str]) -> list[str]:
    """Return the URL endpoints corresponding to the input log file paths."""
    return [_get_log_file_endpoint(log_file) for log_file in log_file_paths]


def _resolve_process_types(
    values: list[str],
) -> list[spectre_server.core.logs.ProcessType]:
    """Convert query-string values to `ProcessType` enums.

    An empty selection defaults to every scope, so the caller sees all logs
    unless they explicitly narrow the request.
    """
    if not values:
        return list(spectre_server.core.logs.ProcessType)
    return [spectre_server.core.logs.ProcessType(v) for v in values]


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
    process_types = _resolve_process_types(flask.request.args.getlist("process_type"))
    log_files = services.get_logs(process_types)
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
    dry_run = flask.request.args.get("dry_run", type=is_true, default=False)
    process_types = _resolve_process_types(flask.request.args.getlist("process_type"))
    log_files = services.delete_logs(process_types, dry_run=dry_run)
    return _get_log_file_endpoints(log_files)
