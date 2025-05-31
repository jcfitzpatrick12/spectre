# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import Blueprint, request
from typing import Any

from ..services import receivers
from ._format_responses import jsendify_response


receivers_blueprint = Blueprint("receivers", __name__, url_prefix="/receivers")


@receivers_blueprint.route("", methods=["GET"])
@jsendify_response
def get_receivers() -> list[str]:
    return receivers.get_registered_receivers()


@receivers_blueprint.route("/<string:receiver_name>/modes", methods=["GET"])
@jsendify_response
def get_modes(receiver_name: str) -> list[str]:
    return receivers.get_modes(receiver_name)


@receivers_blueprint.route("/<string:receiver_name>/specs", methods=["GET"])
@jsendify_response
def get_specs(receiver_name: str) -> dict[str, float | int | list[float | int]]:
    return receivers.get_specs(receiver_name)


@receivers_blueprint.route("/<string:receiver_name>/capture-template", methods=["GET"])
@jsendify_response
def get_capture_template(receiver_name: str) -> dict[str, Any]:
    receiver_mode = request.args.get("receiver_mode", type=str)
    if receiver_mode is None:
        raise ValueError(f"The receiver mode must be specified. Got {receiver_mode}")
    return receivers.get_capture_template(receiver_name, receiver_mode)
