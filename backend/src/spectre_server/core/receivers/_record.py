# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing

import spectre_server.core.jobs
import spectre_server.core.logs

from ._factory import get_receiver
from ._config import Config


def _make_flowgraph_worker(
    config: Config,
    skip_validation: bool,
    spectre_data_dir_path: typing.Optional[str],
) -> spectre_server.core.jobs.Worker:
    receiver = get_receiver(config.receiver_name, config.receiver_mode)
    return spectre_server.core.jobs.make_worker(
        "flowgraph",
        receiver.activate_flowgraph,
        (config.tag, config.parameters, skip_validation),
        spectre_data_dir_path=spectre_data_dir_path,
    )


def _make_post_processing_worker(
    config: Config,
    skip_validation: bool,
    spectre_data_dir_path: typing.Optional[str],
) -> spectre_server.core.jobs.Worker:
    receiver = get_receiver(config.receiver_name, config.receiver_mode)
    return spectre_server.core.jobs.make_worker(
        "post_processing",
        receiver.activate_post_processing,
        (config.tag, config.parameters, skip_validation),
        spectre_data_dir_path=spectre_data_dir_path,
    )


@spectre_server.core.logs.log_call
def record_signal(
    configs: list[Config],
    duration: float = 60,
    force_restart: bool = False,
    max_restarts: int = 5,
    skip_validation: bool = False,
    spectre_data_dir_path: typing.Optional[str] = None,
) -> int:
    """Capture data from SDRs in real time.

    :param config: A list of configs.
    :param duration: How long to record for, in seconds.
    :param force_restart: If specified, restart the recording if it fails at runtime.
    :param max_restarts: Maximum number of times the recording can be restarted before giving up.
    Only applies when force_restart is True. Defaults to 5.
    :param skip_validation: If True, skip validating the config parameters against the model.
    :return: 0 exit code on success.
    """
    flowgraph_workers = [
        _make_flowgraph_worker(config, skip_validation, spectre_data_dir_path)
        for config in configs
    ]
    spectre_server.core.jobs.start_job(
        flowgraph_workers, duration, force_restart, max_restarts
    )

    return 0


@spectre_server.core.logs.log_call
def record_spectrograms(
    configs: list[Config],
    duration: float = 60,
    force_restart: bool = False,
    max_restarts: int = 5,
    skip_validation: bool = False,
    spectre_data_dir_path: typing.Optional[str] = None,
) -> int:
    """Capture data from SDRs and post-process it into spectrograms in real time.

    :param configs: A list of configs.
    :param duration: How long to record for, in seconds.
    :param force_restart: If specified, restart the recording if it fails at runtime.
    :param max_restarts: Maximum number of times the recording can be restarted before giving up.
    Only applies when force_restart is True. Defaults to 5.
    :param skip_validation: If True, skip validating the config parameters against the model.
    :return: 0 exit code on success.
    """
    flowgraph_workers = [
        _make_flowgraph_worker(config, skip_validation, spectre_data_dir_path)
        for config in configs
    ]
    post_processing_workers = [
        _make_post_processing_worker(config, skip_validation, spectre_data_dir_path)
        for config in configs
    ]
    spectre_server.core.jobs.start_job(
        post_processing_workers + flowgraph_workers,
        duration=duration,
        force_restart=force_restart,
        max_restarts=max_restarts,
    )

    return 0
