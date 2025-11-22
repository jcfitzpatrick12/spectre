# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import typing

import flask

from ..services import configs as services
from ._format_responses import jsendify_response, serve_from_directory
from ._utils import is_true


configs_blueprint = flask.Blueprint(
    "configs", __name__, url_prefix="/spectre-data/configs"
)


def _get_config_endpoint(
    config_file_path: str,
) -> str:
    """Return the URL endpoint corresponding to the config at the input path."""
    return flask.url_for(
        "configs.get_config",
        file_name=os.path.basename(config_file_path),
    )


def _get_config_file_endpoints(
    config_file_paths: list[str],
) -> list[str]:
    """Return the URL endpoints corresponding to the input config paths."""
    return [
        _get_config_endpoint(config_file_path) for config_file_path in config_file_paths
    ]


@configs_blueprint.route("/<string:file_name>/raw", methods=["GET"])
@jsendify_response
def get_config_raw(
    file_name: str,
) -> dict[str, typing.Any]:
    return services.get_config_raw(file_name)


@configs_blueprint.route("/<string:file_name>", methods=["GET"])
def get_config(file_name: str) -> flask.Response:
    return serve_from_directory(services.get_config(file_name))


@configs_blueprint.route("/", methods=["GET"])
@jsendify_response
def get_configs() -> list[str]:
    config_file_paths = services.get_configs()
    return _get_config_file_endpoints(config_file_paths)


@configs_blueprint.route("/<string:file_name>", methods=["PUT"])
@jsendify_response
def create_config(file_name: str) -> str:
    json = flask.request.get_json()
    receiver_name = json.get("receiver_name")
    receiver_mode = json.get("receiver_mode")
    string_parameters = json.get("string_parameters")
    force = json.get("force")
    validate = json.get("validate")

    config_file_path = services.create_config(
        file_name,
        receiver_name,
        receiver_mode,
        string_parameters,
        force=force,
        validate=validate,
    )

    return _get_config_endpoint(config_file_path)


@configs_blueprint.route("/<string:file_name>", methods=["DELETE"])
@jsendify_response
def delete_config(file_name: str) -> str:
    dry_run = flask.request.args.get("dry_run", type=is_true, default=False)
    config_file_path = services.delete_config(file_name, dry_run=dry_run)
    return _get_config_endpoint(config_file_path)


@configs_blueprint.route("/<string:file_name>", methods=["PATCH"])
@jsendify_response
def update_config(file_name: str) -> str:
    json = flask.request.get_json()
    string_parameters = json.get("params")
    force = json.get("force")
    validate = json.get("validate")

    config_file_path = services.update_config(
        file_name, string_parameters, force=force, validate=validate
    )

    return _get_config_endpoint(config_file_path)
