# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing
import flask

import spectre_server.core.jobs

from ..services import recordings as services
from ._format_responses import jsendify_response

recordings_blueprint = flask.Blueprint("recordings", __name__, url_prefix="/recordings")


def _get_recording_endpoint(id: str) -> str:
    return flask.url_for("recordings.get_recording", id=id, _external=True)


def _get_worker_endpoint(id: str, name: str) -> str:
    return flask.url_for("recordings.get_worker", id=id, name=name, _external=True)


@recordings_blueprint.route("/", methods=["POST"])
@jsendify_response
def create_recording() -> str:
    json = flask.request.get_json()
    recording_id = services.create_recording(
        tag=json.get("tag"),
        kind=json.get("kind"),
        duration=json.get("duration"),
        force_restart=json.get("force_restart", False),
        max_restarts=json.get("max_restarts", 5),
        validate=json.get("validate", True),
    )
    return _get_recording_endpoint(recording_id)


@recordings_blueprint.route("/", methods=["GET"])
@jsendify_response
def get_recordings() -> list[str]:
    values = flask.request.args.getlist("state")
    states = [spectre_server.core.jobs.RecordingState(v) for v in values]
    ids = services.get_recordings(states)
    return [_get_recording_endpoint(id) for id in ids]


@recordings_blueprint.route("/<string:id>", methods=["GET"])
@jsendify_response
def get_recording(id: str) -> dict[str, typing.Any]:
    return services.get_recording(id)


@recordings_blueprint.route("/<string:id>", methods=["PATCH"])
@jsendify_response
def update_recording(id: str) -> str:
    json = flask.request.get_json()
    stop_requested = json.get("stop_requested", False)
    if stop_requested:
        _ = services.stop_recording(id)
    return _get_recording_endpoint(id)


@recordings_blueprint.route("/<string:id>", methods=["DELETE"])
@jsendify_response
def delete_recording(id: str) -> str:
    recording_id = services.delete_recording(id)
    return _get_recording_endpoint(recording_id)


@recordings_blueprint.route("/<string:id>/workers", methods=["GET"])
@jsendify_response
def get_workers(id: str) -> list[str]:
    names = services.get_workers(id)
    return [_get_worker_endpoint(id, name) for name in names]


@recordings_blueprint.route("/<string:id>/workers/<string:name>", methods=["GET"])
@jsendify_response
def get_worker(id: str, name: str) -> dict[str, typing.Any]:
    return services.get_worker(id, name)


@recordings_blueprint.route("/<string:id>/workers/<string:name>/log", methods=["GET"])
@jsendify_response
def get_worker_log(id: str, name: str) -> str:
    return services.get_worker_log(id, name)
