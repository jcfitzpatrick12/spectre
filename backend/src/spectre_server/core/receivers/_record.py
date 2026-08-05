# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing

import spectre_server.core.jobs

from ._factory import get_receiver
from ._config import Config


def make_flowgraph_worker(
    config: Config,
    skip_validation: bool,
    spectre_data_dir_path: typing.Optional[str] = None,
    on_start: typing.Optional[typing.Callable[[int], None]] = None,
) -> spectre_server.core.jobs.Worker:
    """Build a `Worker` that runs a receiver's flowgraph for a given config.

    Not started; the caller must invoke `start()` on the returned worker (or
    hand it to a `Job`).

    :param on_start: Optional callback invoked with the worker's PID after
        every successful start (including restarts).
    """
    receiver = get_receiver(config.receiver_name, config.receiver_mode)
    return spectre_server.core.jobs.make_worker(
        "flowgraph",
        receiver.activate_flowgraph,
        (config.tag, config.parameters, skip_validation),
        spectre_data_dir_path=spectre_data_dir_path,
        on_start=on_start,
    )


def make_post_processing_worker(
    config: Config,
    skip_validation: bool,
    spectre_data_dir_path: typing.Optional[str] = None,
    on_start: typing.Optional[typing.Callable[[int], None]] = None,
) -> spectre_server.core.jobs.Worker:
    """Build a `Worker` that runs a receiver's post-processing for a config.

    Not started; the caller must invoke `start()` on the returned worker (or
    hand it to a `Job`).

    :param on_start: Optional callback invoked with the worker's PID after
        every successful start (including restarts).
    """
    receiver = get_receiver(config.receiver_name, config.receiver_mode)
    return spectre_server.core.jobs.make_worker(
        "post_processing",
        receiver.activate_post_processing,
        (config.tag, config.parameters, skip_validation),
        spectre_data_dir_path=spectre_data_dir_path,
        on_start=on_start,
    )
