# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""HTTP routes for recording lifecycle management.

All responses are JSend-compliant. Successful responses put the resource
URL(s) — or, for a single-resource GET, the resource properties — directly
in ``data``. Anything else — bad input, unknown id, state conflict — is
raised as a plain exception in the service layer and surfaced as a JSend
``error`` response by the ``jsendify_response`` wrapper.
"""

import typing

import flask

from ..services import recordings as services
from ._format_responses import jsendify_response

recordings_blueprint = flask.Blueprint(
    "recordings", __name__, url_prefix="/recordings"
)


def _recording_url(id: str) -> str:
    """Return the resource URL for a recording."""
    return flask.url_for("recordings.get_recording", id=id, _external=True)


def _recording_urls(ids: list[str]) -> list[str]:
    return [_recording_url(rid) for rid in ids]


@recordings_blueprint.route("", methods=["POST"])
@jsendify_response
def create_recording() -> list[str]:
    """Create one recording per tag and start each supervisor.

    Body::

        {
            "kind": "signal" | "spectrogram",
            "tags": ["tag-a", "tag-b"],
            "duration": 30.0,
            "force_restart": false,
            "max_restarts": 5,
            "validate": true
        }

    Returns the URLs of the created recordings, in the order the tags were
    supplied. Clients GET each URL to observe progress.
    """
    json = flask.request.get_json(silent=True) or {}
    ids = services.create_recording(
        kind=json.get("kind"),
        tags=json.get("tags") or [],
        duration=json.get("duration"),
        force_restart=bool(json.get("force_restart", False)),
        max_restarts=int(json.get("max_restarts", 5)),
        validate=bool(json.get("validate", True)),
    )
    return _recording_urls(ids)


@recordings_blueprint.route("", methods=["GET"])
@jsendify_response
def list_recordings() -> list[str]:
    """List recording URLs, optionally filtered by state, tag, and/or kind."""
    ids = services.list_recordings(
        state=flask.request.args.get("state"),
        tag=flask.request.args.get("tag"),
        kind=flask.request.args.get("kind"),
    )
    return _recording_urls(ids)


@recordings_blueprint.route("/<string:id>", methods=["GET"])
@jsendify_response
def get_recording(id: str) -> dict[str, typing.Any]:
    """Return the properties of a single recording."""
    return services.get_recording(id)


@recordings_blueprint.route("/<string:id>", methods=["PATCH"])
@jsendify_response
def patch_recording(id: str) -> str:
    """Request a state transition for a recording.

    Body::

        {"state": "stopped"}

    Currently only ``stopped`` may be requested; other states are set by the
    system. Returns the URL of the patched resource so the client can GET
    it to observe the outcome.
    """
    json = flask.request.get_json(silent=True) or {}
    services.request_state(id, json.get("state"))
    return _recording_url(id)


@recordings_blueprint.route("/<string:id>", methods=["DELETE"])
@jsendify_response
def delete_recording(id: str) -> str:
    """Delete a terminal recording. Returns the URL of the deleted resource."""
    services.delete_recording(id)
    return _recording_url(id)


def _worker_url(recording_id: str, worker_id: int) -> str:
    return flask.url_for(
        "recordings.get_worker",
        id=recording_id,
        worker_id=worker_id,
        _external=True,
    )


@recordings_blueprint.route("/<string:id>/workers", methods=["GET"])
@jsendify_response
def list_workers(id: str) -> list[str]:
    """List worker URLs for a recording, in the order they were registered."""
    return [
        _worker_url(id, wid) for wid in services.list_workers(id)
    ]


@recordings_blueprint.route(
    "/<string:id>/workers/<int:worker_id>", methods=["GET"]
)
@jsendify_response
def get_worker(id: str, worker_id: int) -> dict[str, typing.Any]:
    """Return worker metadata under a recording."""
    return services.get_worker(id, worker_id)


@recordings_blueprint.route(
    "/<string:id>/workers/<int:worker_id>/logs", methods=["GET"]
)
@jsendify_response
def get_worker_log(id: str, worker_id: int) -> str:
    """Return the raw text of the log the worker wrote."""
    return services.get_worker_log(id, worker_id)


# ---------------------------------------------------------------------------
# Backwards-compatible endpoints.
#
# These preserve the pre-issue-192 behaviour where the client `POST`s to
# `/recordings/signal` or `/recordings/spectrogram` and the request blocks
# until the recording finishes. They are thin wrappers around the same
# supervisor plumbing used by the new endpoints, so BC recordings are also
# visible in `GET /recordings` and can be deleted through the new API.
# ---------------------------------------------------------------------------


@recordings_blueprint.route("/signal", methods=["POST"])
@jsendify_response
def signal() -> int:
    json = flask.request.get_json(silent=True) or {}
    return services.signal(
        tags=json.get("tags") or [],
        duration=json.get("duration"),
        force_restart=bool(json.get("force_restart", False)),
        max_restarts=int(json.get("max_restarts", 5)),
        validate=bool(json.get("validate", True)),
    )


@recordings_blueprint.route("/spectrogram", methods=["POST"])
@jsendify_response
def spectrograms() -> int:
    json = flask.request.get_json(silent=True) or {}
    return services.spectrograms(
        tags=json.get("tags") or [],
        duration=json.get("duration"),
        force_restart=bool(json.get("force_restart", False)),
        max_restarts=int(json.get("max_restarts", 5)),
        validate=bool(json.get("validate", True)),
    )
