# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import Blueprint, request

from spectre_server.services import configs
from spectre_server.routes import jsendify_response


configs_blueprint = Blueprint("configs", __name__)


@configs_blueprint.route("", methods=["GET"])
@jsendify_response
def get_configs():
    return configs.get_configs()


@configs_blueprint.route("fits-configs", methods=["GET"])
@jsendify_response
def get_fits_configs():
    return configs.get_configs(config_type = "fits_config")


@configs_blueprint.route("capture-configs", methods=["GET"])
@jsendify_response
def get_capture_configs():
    return configs.get_configs(config_type = "capture_config")


@configs_blueprint.route("/fits-configs/<string:tag>", methods=["PUT"])
@jsendify_response
def create_fits_config(tag: str):
    payload = request.get_json()
    params = payload.get("params")
    force = payload.get("force")
    return configs.create_fits_config(tag, 
                                      params,
                                      force)


@configs_blueprint.route("/capture-configs/<string:tag>", methods=["PUT"])
@jsendify_response
def create_capture_config(tag: str):
    payload = request.get_json()
    receiver_name = payload.get("receiver_name")
    mode = payload.get("mode")
    params = payload.get("params")
    force = payload.get("force")
    return configs.create_capture_config(tag, 
                                         receiver_name,
                                         mode,
                                         params,
                                         force)


@configs_blueprint.route("/fits-configs/<string:tag>", methods=["DELETE"])
@jsendify_response
def delete_fits_config(tag: str):
    return configs.delete_fits_config(tag)


@configs_blueprint.route("/capture-configs/<string:tag>", methods=["DELETE"])
@jsendify_response
def delete_capture_config(tag: str):
    return configs.delete_fits_config(tag)


@configs_blueprint.route("/fits-configs/<string:tag>", methods=["GET"])
@jsendify_response
def fits_config(tag: str):
    return configs.get_fits_config(tag)


@configs_blueprint.route("/capture-configs/<string:tag>", methods=["GET"])
@jsendify_response
def capture_config(tag: str):
    return configs.get_capture_config(tag)