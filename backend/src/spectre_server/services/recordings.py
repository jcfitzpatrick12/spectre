# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import multiprocessing
import os

import spectre_core.logs
import spectre_core.receivers

from . import jobs as job_services


@spectre_core.logs.log_call
def signal(
    tags: list[str],
    duration: float,
    force_restart: bool = False,
    max_restarts: int = 5,
    validate: bool = True,
) -> int:
    """Capture data from an SDR in real time.

    :param tags: A bundle of config tags.
    :param duration: How long to record the signal for, in seconds.
    :param force_restart: If specified, restart all workers if one dies unexpectedly.
    :param max_restarts: Maximum number of times workers can be restarted before giving up and killing all workers.
    Only applies when force_restart is True. Defaults to 5.
    :param validate: If True, validate the config parameters. Defaults to True.
    :return: A string indicating the job has completed.
    """
    configs = [spectre_core.receivers.read_config(tag) for tag in tags]
    return spectre_core.receivers.record_signal(
        configs, duration, force_restart, max_restarts, skip_validation=not validate
    )


@spectre_core.logs.log_call
def spectrograms(
    tags: list[str],
    duration: float,
    force_restart: bool = False,
    max_restarts: int = 5,
    validate: bool = True,
) -> int:
    """Capture data from an SDR and post-process it into spectrograms in real time.

    :param tags: A bundle of config tags.
    :param duration: How long to record the spectrograms for, in seconds.
    :param force_restart: If specified, restart all workers if one dies unexpectedly.
    :param max_restarts: Maximum number of times workers can be restarted before giving up and killing all workers.
    Only applies when force_restart is True. Defaults to 5.
    :param validate: If True, validate the config parameters. Defaults to True.
    :return: A string indicating the job has completed.
    """
    configs = [spectre_core.receivers.read_config(tag) for tag in tags]
    return spectre_core.receivers.record_spectrograms(
        configs, duration, force_restart, max_restarts, skip_validation=not validate
    )


def _run_recording_worker(
    job_id: str,
    tags: list[str],
    duration: float,
    force_restart: bool,
    max_restarts: int,
    validate: bool,
) -> None:
    """Worker function that runs the recording in a separate process.

    This function updates the job status as it progresses.
    """
    try:
        # Mark job as running
        job_services.update_job(job_id, status=job_services.JobStatus.RUNNING.value)

        # Run the actual recording (this blocks for the duration)
        configs = [spectre_core.receivers.read_config(tag) for tag in tags]
        exit_code = spectre_core.receivers.record_spectrograms(
            configs, duration, force_restart, max_restarts, skip_validation=not validate
        )

        if exit_code == 0:
            # Recording completed successfully
            job_services.update_job(
                job_id,
                status=job_services.JobStatus.COMPLETED.value,
                progress=100.0,
            )
        else:
            # Recording failed
            job_services.update_job(
                job_id,
                status=job_services.JobStatus.FAILED.value,
                error=f"Recording failed with exit code {exit_code}",
            )

    except Exception as e:
        # Recording crashed
        job_services.update_job(
            job_id,
            status=job_services.JobStatus.FAILED.value,
            error=str(e),
        )


def spectrograms_async(
    tags: list[str],
    duration: float,
    force_restart: bool = False,
    max_restarts: int = 5,
    validate: bool = True,
) -> job_services.Job:
    """Start an async spectrogram recording job.

    Returns immediately with a job ID while the recording runs in the background.

    :param tags: A bundle of config tags.
    :param duration: How long to record the spectrograms for, in seconds.
    :param force_restart: If specified, restart all workers if one dies unexpectedly.
    :param max_restarts: Maximum number of times workers can be restarted before giving up and killing all workers.
    Only applies when force_restart is True. Defaults to 5.
    :param validate: If True, validate the config parameters. Defaults to True.
    :return: Job instance with job_id
    """
    # Create a new job
    # Use first tag for job metadata
    tag = tags[0] if tags else "unknown"
    job = job_services.create_job(tag, duration)

    # Spawn a background process to run the recording
    process = multiprocessing.Process(
        target=_run_recording_worker,
        args=(job.job_id, tags, duration, force_restart, max_restarts, validate),
    )
    process.start()

    # Update job with process ID
    job_services.update_job(job.job_id, pid=process.pid)

    # Return the job (with job_id) immediately
    return job_services.get_job(job.job_id)
