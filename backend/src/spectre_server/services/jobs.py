# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre_core.logs import log_call
from spectre_core.capture_configs import CaptureConfig
from spectre_core.receivers import get_receiver, ReceiverName
from spectre_core.post_processing import start_post_processor
from spectre_core import jobs


def _calculate_total_runtime(
    seconds: int = 0, minutes: int = 0, hours: int = 0
) -> float:
    total_duration = seconds + (minutes * 60) + (hours * 3600)  # [s]
    if total_duration <= 0:
        raise ValueError(f"Total duration must be strictly positive.")
    return total_duration


# Decorate with `log_call`, so that log records are written to file if the function errors out when called by a worker.
@log_call
def _start_post_processing(tag: str) -> None:
    start_post_processor(tag)


# Decorate with `log_call`, so that log records are written to file if the function errors out when called by a worker.
@log_call
def _start_capture(tag: str, skip_validation: bool = False) -> None:
    # load the receiver and mode from the capture config file
    capture_config = CaptureConfig(tag)

    # start capturing data from the receiver.
    name = ReceiverName(capture_config.receiver_name)
    receiver = get_receiver(name, capture_config.receiver_mode)
    receiver.start_capture(tag, skip_validation)


@log_call
def capture(
    tag: str,
    seconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    force_restart: bool = False,
    max_restarts: int = 5,
    skip_validation: bool = False,
) -> str:
    """Start capturing data from an SDR in real time.

    :param tag: The capture config tag.
    :param seconds: The seconds component of the total runtime, defaults to 0
    :param minutes: The minutes component of the total runtime, defaults to 0
    :param hours: The hours component of the total runtime, defaults to 0
    :param force_restart: Whether to restart all workers if one dies unexpectedly.
    :param max_restarts: Maximum number of times workers can be restarted before giving up and killing all workers.
    Only applies when force_restart is True. Defaults to 5.
    :param skip_validation: If True, skip validating the capture config. Defaults to False.
    :return: A string indicating the job has completed.
    """
    # Trailing commas are required so that the bracket terms are interpreted as tuples, not a grouping.
    capture_worker = jobs.make_worker(
        "capture_worker", _start_capture, (tag, skip_validation)
    )
    workers = [capture_worker]
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)
    jobs.start_job(workers, total_runtime, force_restart, max_restarts)
    return "Capture complete."


@log_call
def session(
    tag: str,
    seconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    force_restart: bool = False,
    max_restarts: int = 5,
    skip_validation: bool = False,
) -> str:
    """Start capturing data from an SDR, and post-process the data in real time into spectrograms.

    :param tag: The capture config tag.
    :param seconds: The seconds component of the total runtime, defaults to 0
    :param minutes: The minutes component of the total runtime, defaults to 0
    :param hours: The hours component of the total runtime, defaults to 0
    :param force_restart: Whether to restart all workers if one dies unexpectedly.
    :param max_restarts: Maximum number of times workers can be restarted before giving up and killing all workers.
    Only applies when force_restart is True. Defaults to 5.
    :param skip_validation: If True, skip validating the capture config. Defaults to False.
    :return: A string indicating the job has completed.
    """
    # Trailing commas are required so that the bracket terms are interpreted as tuples, not a grouping.
    post_processing_worker = jobs.make_worker(
        "post_processing_worker", _start_post_processing, (tag,)
    )
    capture_worker = jobs.make_worker("capture_worker", _start_capture, (tag, skip_validation,))

    # start the post processing worker first, so that it sees the first files opened by the capture worker.
    workers = [post_processing_worker, capture_worker]
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)
    jobs.start_job(workers, total_runtime, force_restart, max_restarts)
    return "Session complete."
