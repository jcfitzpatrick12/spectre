# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import Blueprint, request
from typing import Any

from spectre_server.services import capture_configs
from spectre_server.routes._format_responses import jsendify_response


capture_configs_blueprint = Blueprint("capture-configs", __name__)


@capture_configs_blueprint.route("", methods=["GET"])
@jsendify_response
def get_capture_configs(
) -> list[str]:
    return capture_configs.get_capture_configs()


@capture_configs_blueprint.route("/<string:tag>", methods=["GET"])
@jsendify_response
def get_capture_config(
    tag: str
) -> dict[str, Any]:
    return capture_configs.get_capture_config(tag)


@capture_configs_blueprint.route("/<string:tag>", methods=["PUT"])
@jsendify_response
def create_capture_config(
    tag: str
) -> str:
    json = request.get_json()
    receiver_name     = json.get("receiver_name")
    receiver_mode     = json.get("receiver_mode")
    string_parameters = json.get("string_parameters")
    force             = json.get("force")
    return capture_configs.create_capture_config(tag, 
                                                 receiver_name,
                                                 receiver_mode,
                                                 string_parameters,
                                                 force)


@capture_configs_blueprint.route("/<string:tag>", methods=["DELETE"])
@jsendify_response
def delete_capture_config(
    tag: str
) -> str:
    return capture_configs.delete_capture_config(tag)


@capture_configs_blueprint.route("/<string:tag>", methods=["PATCH"])
@jsendify_response
def update_capture_config(
    tag: str
) -> str:
    json              = request.get_json()
    string_parameters = json.get("params")
    force             = json.get("force")
    return capture_configs.update_capture_config(tag, 
                                                 string_parameters,
                                                 force)