# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from os.path import basename
from flask import Blueprint, request, Response, url_for
from typing import Any

from ..services import capture_configs
from ._format_responses import jsendify_response, serve_from_directory


capture_configs_blueprint = Blueprint("capture_configs", __name__, url_prefix="/spectre-data/configs")


@capture_configs_blueprint.route("/<string:base_file_name>/raw", methods=["GET"])
@jsendify_response
def get_capture_config_raw(
    base_file_name: str,
) -> dict[str, Any]:
    return capture_configs.read_capture_config(base_file_name)


@capture_configs_blueprint.route("/<string:base_file_name>", methods=["GET"])
@jsendify_response
def get_capture_config(
    base_file_name: str
) -> Response:
    return serve_from_directory( capture_configs.get_capture_config(base_file_name) )


@capture_configs_blueprint.route("/", methods=["GET"])
@jsendify_response
def get_capture_configs(
) -> list[str]:
    base_file_names = capture_configs.get_capture_configs()

    resource_endpoints = []
    for base_file_name in base_file_names:
        resource_endpoint = url_for("capture_configs.get_capture_config",
                                    base_file_name=basename(base_file_name),
                                    _external=True)
        resource_endpoints.append(resource_endpoint)
        
    return resource_endpoints


@capture_configs_blueprint.route("/<string:base_file_name>", methods=["PUT"])
@jsendify_response
def create_capture_config(
    base_file_name: str
) -> str:
    json = request.get_json()
    receiver_name     = json.get("receiver_name")
    receiver_mode     = json.get("receiver_mode")
    string_parameters = json.get("string_parameters")
    force             = json.get("force")

    capture_configs.create_capture_config(base_file_name, 
                                          receiver_name,
                                          receiver_mode,
                                          string_parameters,
                                          force)

    return url_for("capture_configs.get_capture_config",
                   base_file_name=base_file_name,
                   _external=True)


@capture_configs_blueprint.route("/<string:base_file_name>", methods=["DELETE"])
@jsendify_response
def delete_capture_config(
    base_file_name: str
) -> str:
    capture_configs.delete_capture_config(base_file_name)
    
    return url_for("capture_configs.get_capture_config",
                   base_file_name=base_file_name,
                   _external=True)


@capture_configs_blueprint.route("/<string:base_file_name>", methods=["PATCH"])
@jsendify_response
def update_capture_config(
    base_file_name: str
) -> str:
    json              = request.get_json()
    string_parameters = json.get("params")
    force             = json.get("force")

    capture_configs.update_capture_config(base_file_name, 
                                          string_parameters,
                                          force)
    
    return url_for("capture_configs.get_capture_config", 
                   base_file_name=base_file_name,
                   _external=True)
