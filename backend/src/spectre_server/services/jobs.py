# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from spectre_core.logging import log_call
from spectre_core import jobs

@log_call
def capture(tag: str, 
            seconds: int = 0, 
            minutes: int = 0, 
            hours: int = 0, 
            force_restart: bool = False
) -> str:
    """Start capturing data from an SDR in real time.

    :param tag: The capture config tag.
    :param seconds: The seconds component of the total runtime, defaults to 0
    :param minutes: The minutes component of the total runtime, defaults to 0
    :param hours: The hours component of the total runtime, defaults to 0
    :param force_restart: If any worker encounters an error at runtime, force all
    the workers to restart their processes. Defaults to False
    :return: A string indicating the job has completed.
    """
    total_runtime = jobs.calculate_total_runtime(seconds, 
                                                 minutes, 
                                                 hours) 
    capture_worker = jobs.capture(tag)
    
    jobs.monitor_workers([capture_worker], 
                         total_runtime, 
                         force_restart)
    return "Capture complete."
                       

@log_call
def session(tag: str, 
            seconds: int = 0, 
            minutes: int = 0, 
            hours: int = 0, 
            force_restart: bool = False
) -> str:
    """Start a `spectre` session.
    
    Start capturing data from an SDR, and post-process the data in real time into spectrograms.

    :param tag: The capture config tag.
    :param seconds: The seconds component of the total runtime, defaults to 0
    :param minutes: The minutes component of the total runtime, defaults to 0
    :param hours: The hours component of the total runtime, defaults to 0
    :param force_restart: If any worker encounters an error at runtime, force all
    the workers to restart their processes. Defaults to False
    """
    total_runtime = jobs.calculate_total_runtime(seconds, 
                                                 minutes, 
                                                 hours)

    capture_worker, post_process_worker = jobs.session(tag)

    jobs.monitor_workers([capture_worker, post_process_worker],
                         total_runtime,
                         force_restart)
    return "Session complete."
    