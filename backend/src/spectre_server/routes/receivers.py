# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import flask
import typing

from ..services import receivers as services
from ._format_responses import jsendify_response


receivers_blueprint = flask.Blueprint("receivers", __name__, url_prefix="/receivers")


@receivers_blueprint.route("", methods=["GET"])
@jsendify_response
def get_receivers() -> list[str]:
    return services.get_receivers()


@receivers_blueprint.route("/<string:receiver_name>/modes", methods=["GET"])
@jsendify_response
def get_modes(receiver_name: str) -> list[str]:
    return services.get_modes(receiver_name)


@receivers_blueprint.route("/<string:receiver_name>/model", methods=["GET"])
@jsendify_response
def get_model(receiver_name: str) -> dict[str, typing.Any]:
    receiver_mode = flask.request.args.get("receiver_mode", type=str)
    if receiver_mode is None:
        raise ValueError(f"The receiver mode must be specified. Got {receiver_mode}")
    return services.get_model(receiver_name, receiver_mode)
