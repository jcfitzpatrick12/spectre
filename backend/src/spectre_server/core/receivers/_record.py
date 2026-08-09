# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing

import spectre_server.core.jobs
import spectre_server.core.logs

from ._factory import get_receiver
from ._config import Config


def make_signal_worker(
    config: Config,
    recording_id: str,
    skip_validation: bool,
    logs_dir_path: typing.Optional[str] = None,
    spectre_data_dir_path: typing.Optional[str] = None,
) -> spectre_server.core.jobs.Worker:
    """Build a `Worker` that runs a receiver's flowgraph for a given config.

    Not started; the caller must invoke `start()` on the returned worker (or
    hand it to a `Job`).
    """
    receiver = get_receiver(config.receiver_name, config.receiver_mode)
    worker_name = spectre_server.core.jobs.WorkerName.SIGNAL.value
    return spectre_server.core.jobs.make_worker(
        worker_name,
        receiver.activate_flowgraph,
        (config.tag, config.parameters, skip_validation),
        log_file_path=spectre_server.core.logs.get_worker_log_file_path(
            recording_id, worker_name, logs_dir_path=logs_dir_path
        ),
        spectre_data_dir_path=spectre_data_dir_path,
    )


def make_spectrograms_worker(
    config: Config,
    recording_id: str,
    skip_validation: bool,
    logs_dir_path: typing.Optional[str] = None,
    spectre_data_dir_path: typing.Optional[str] = None,
) -> spectre_server.core.jobs.Worker:
    """Build a `Worker` that runs a receiver's post-processing for a config.

    Not started; the caller must invoke `start()` on the returned worker (or
    hand it to a `Job`).
    """
    receiver = get_receiver(config.receiver_name, config.receiver_mode)
    worker_name = spectre_server.core.jobs.WorkerName.SPECTROGRAM.value
    return spectre_server.core.jobs.make_worker(
        worker_name,
        receiver.activate_post_processing,
        (config.tag, config.parameters, skip_validation),
        log_file_path=spectre_server.core.logs.get_worker_log_file_path(
            recording_id, worker_name, logs_dir_path=logs_dir_path
        ),
        spectre_data_dir_path=spectre_data_dir_path,
    )
