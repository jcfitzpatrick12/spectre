# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre_core.logs import log_call
from spectre_core.capture_configs import CaptureConfig
from spectre_core.receivers import get_receiver, ReceiverName
from spectre_core.post_processing import start_post_processor
from spectre_core import jobs

DONE = "Done"


def _calculate_total_runtime(
    seconds: int = 0, minutes: int = 0, hours: int = 0
) -> float:
    total_duration = seconds + (minutes * 60) + (hours * 3600)  # [s]
    if total_duration <= 0:
        raise ValueError(f"Total duration must be strictly positive.")
    return total_duration


# Decorate with `log_call`, so that log records are written to file if the function errors out when called by a worker.
@log_call
def _post_process(tag: str) -> None:
    start_post_processor(tag)


# Decorate with `log_call`, so that log records are written to file if the function errors out when called by a worker.
@log_call
def _record_signal(tag: str, validate: bool = True) -> None:
    capture_config = CaptureConfig(tag)
    name = ReceiverName(capture_config.receiver_name)
    receiver = get_receiver(name, capture_config.receiver_mode)
    receiver.start_capture(tag, validate)


@log_call
def signal(
    tag: str,
    seconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    force_restart: bool = False,
    max_restarts: int = 5,
    validate: bool = True,
) -> str:
    """Capture data from an SDR in real time.

    :param tag: The capture config tag.
    :param seconds: The seconds component of the job duration., defaults to 0
    :param minutes: The minutes component of the job duration, defaults to 0
    :param hours: The hours component of the job duration, defaults to 0
    :param force_restart: If specified, restart all workers if one dies unexpectedly.
    :param max_restarts: Maximum number of times workers can be restarted before giving up and killing all workers.
    Only applies when force_restart is True. Defaults to 5.
    :param validate: If True, validate the capture config parameters. Defaults to True.
    :return: A string indicating the job has completed.
    """
    signal_recorder = jobs.make_worker(
        "signal_recorder",
        _record_signal,
        (
            tag,
            validate,
        ),
    )
    workers = [signal_recorder]
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)
    jobs.start_job(workers, total_runtime, force_restart, max_restarts)
    return DONE


@log_call
def spectrograms(
    tag: str,
    seconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    force_restart: bool = False,
    max_restarts: int = 5,
    validate: bool = True,
) -> str:
    """Capture data from an SDR and post-process it into spectrograms in real time.

    :param tag: The capture config tag.
    :param seconds: The seconds component of the job duration, defaults to 0
    :param minutes: The minutes component of the job duration, defaults to 0
    :param hours: The hours component of the job duration, defaults to 0
    :param force_restart: If specified, restart all workers if one dies unexpectedly.
    :param max_restarts: Maximum number of times workers can be restarted before giving up and killing all workers.
    Only applies when force_restart is True. Defaults to 5.
    :param validate: If True, validate the capture config parameters. Defaults to True.
    :return: A string indicating the job has completed.
    """
    # Trailing commas are required so that the bracket terms are interpreted as tuples, not a grouping.
    post_processer = jobs.make_worker("post_processer", _post_process, (tag,))
    signal_recorder = jobs.make_worker(
        "signal_recorder",
        _record_signal,
        (
            tag,
            validate,
        ),
    )

    # Start the spectrogram recorder
    workers = [post_processer, signal_recorder]
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)
    jobs.start_job(workers, total_runtime, force_restart, max_restarts)
    return DONE
