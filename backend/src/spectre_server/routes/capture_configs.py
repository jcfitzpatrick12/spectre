# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from os.path import basename
from flask import Blueprint, request, Response, url_for
from typing import Any

from ..services import capture_configs
from ._format_responses import jsendify_response, serve_from_directory


capture_configs_blueprint = Blueprint(
    "capture_configs", __name__, url_prefix="/spectre-data/configs"
)


def _get_capture_config_endpoint(
    capture_config_file_path: str,
) -> str:
    """Return the URL endpoint corresponding to the capture config at the input path."""
    return url_for(
        "capture_configs.get_capture_config",
        file_name=basename(capture_config_file_path),
        _external=True,
    )


def _get_capture_config_file_endpoints(
    capture_config_file_paths: list[str],
) -> list[str]:
    """Return the URL endpoints corresponding to the input capture config paths."""
    return [
        _get_capture_config_endpoint(capture_config_file_path)
        for capture_config_file_path in capture_config_file_paths
    ]


@capture_configs_blueprint.route("/<string:file_name>/raw", methods=["GET"])
@jsendify_response
def get_capture_config_raw(
    file_name: str,
) -> dict[str, Any]:
    return capture_configs.read_capture_config(file_name)


@capture_configs_blueprint.route("/<string:file_name>", methods=["GET"])
@jsendify_response
def get_capture_config(file_name: str) -> Response:
    return serve_from_directory(capture_configs.get_capture_config(file_name))


@capture_configs_blueprint.route("/", methods=["GET"])
@jsendify_response
def get_capture_configs() -> list[str]:
    capture_config_file_paths = capture_configs.get_capture_configs()
    return _get_capture_config_file_endpoints(capture_config_file_paths)


@capture_configs_blueprint.route("/<string:file_name>", methods=["PUT"])
@jsendify_response
def create_capture_config(file_name: str) -> str:
    json = request.get_json()
    receiver_name = json.get("receiver_name")
    receiver_mode = json.get("receiver_mode")
    string_parameters = json.get("string_parameters")
    force = json.get("force")

    capture_config_file_path = capture_configs.create_capture_config(
        file_name, receiver_name, receiver_mode, string_parameters, force
    )

    return _get_capture_config_endpoint(capture_config_file_path)


@capture_configs_blueprint.route("/<string:file_name>", methods=["DELETE"])
@jsendify_response
def delete_capture_config(file_name: str) -> str:
    capture_config_file_path = capture_configs.delete_capture_config(file_name)
    return _get_capture_config_endpoint(capture_config_file_path)


@capture_configs_blueprint.route("/<string:file_name>", methods=["PATCH"])
@jsendify_response
def update_capture_config(file_name: str) -> str:
    json = request.get_json()
    string_parameters = json.get("params")
    force = json.get("force")

    capture_config_file_path = capture_configs.update_capture_config(
        file_name, string_parameters, force
    )

    return _get_capture_config_endpoint(capture_config_file_path)
