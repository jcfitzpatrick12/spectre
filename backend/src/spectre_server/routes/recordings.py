# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import flask

from ..services import recordings as services
from ..services import jobs as job_services
from ._format_responses import jsendify_response


recordings_blueprint = flask.Blueprint("recordings", __name__, url_prefix="/recordings")


@recordings_blueprint.route("/signal", methods=["POST"])
@jsendify_response
def signal() -> int:
    json = flask.request.get_json()
    tags = json.get("tags")
    duration = json.get("duration")
    force_restart = json.get("force_restart")
    max_restarts = json.get("max_restarts")
    validate = json.get("validate")
    return services.signal(tags, duration, force_restart, max_restarts, validate)


@recordings_blueprint.route("/spectrogram", methods=["POST"])
@jsendify_response
def spectrograms() -> int:
    json = flask.request.get_json()
    tags = json.get("tags")
    duration = json.get("duration")
    force_restart = json.get("force_restart")
    max_restarts = json.get("max_restarts")
    validate = json.get("validate")
    return services.spectrograms(tags, duration, force_restart, max_restarts, validate)


@recordings_blueprint.route("/spectrogram/async", methods=["POST"])
@jsendify_response
def spectrograms_async() -> dict:
    """Start an async spectrogram recording job.

    Returns job_id immediately while recording continues in background.
    """
    json = flask.request.get_json()
    tags = json.get("tags")
    duration = json.get("duration")
    force_restart = json.get("force_restart")
    max_restarts = json.get("max_restarts")
    validate = json.get("validate")

    job = services.spectrograms_async(tags, duration, force_restart, max_restarts, validate)
    return job.to_dict()


@recordings_blueprint.route("/jobs/<job_id>", methods=["GET"])
@jsendify_response
def get_job_status(job_id: str) -> dict:
    """Get the status of a recording job."""
    job = job_services.get_job(job_id)

    if not job:
        flask.abort(404, description=f"Job {job_id} not found")

    # Update progress based on elapsed time
    progress = job_services.calculate_progress(job)

    # Check if process is still running
    if job.status == job_services.JobStatus.RUNNING.value:
        if not job_services.is_process_running(job.pid):
            # Process died unexpectedly
            job_services.update_job(
                job_id,
                status=job_services.JobStatus.FAILED.value,
                error="Recording process terminated unexpectedly"
            )
            job = job_services.get_job(job_id)
        else:
            # Update progress
            job_services.update_job(job_id, progress=progress)
            job = job_services.get_job(job_id)

    return job.to_dict()


@recordings_blueprint.route("/jobs", methods=["GET"])
@jsendify_response
def list_jobs() -> list[dict]:
    """List all recording jobs."""
    limit = flask.request.args.get("limit", type=int)
    jobs = job_services.list_jobs(limit=limit)
    return [job.to_dict() for job in jobs]


@recordings_blueprint.route("/jobs/<job_id>", methods=["DELETE"])
@jsendify_response
def cancel_job(job_id: str) -> dict:
    """Cancel a running job."""
    success = job_services.cancel_job(job_id)

    if not success:
        flask.abort(404, description=f"Job {job_id} not found or cannot be cancelled")

    return {"job_id": job_id, "cancelled": True}
