# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import spectre_core.logs
import spectre_core.receivers


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
